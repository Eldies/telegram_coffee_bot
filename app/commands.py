# -*- coding: utf-8 -*-
from enum import Enum
import logging

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from .exceptions import GoogleApiError
from .google_maps import get_city_data
from .mongo import get_users_collection


logger = logging.getLogger(__name__)


class ConversationStatus(Enum):
    city = 1
    city_confirm = 2


YES = 'Да'
NO = 'Нет'


def start(update: Update, context: CallbackContext) -> ConversationStatus:
    user = update.effective_user
    logger.info("User {} (id: {}) started conversation.".format(user.name, user.id))
    collection = get_users_collection()
    item = collection.find_one(dict(_id=user.id))
    if item is None:
        collection.insert_one(dict(_id=user.id))

    update.message.reply_text(
        'Привет, {}!\n'
        'Я постараюсь найти группу людей, с которыми Вам удобно встретиться.'
        'Введите /delete если передумаете.\n\n'
        'В каком городе Вы находитесь?'.format(user.name),
    )

    return ConversationStatus.city


def city(update: Update, context: CallbackContext) -> ConversationStatus | int:
    user = update.effective_user
    logger.info("User {} (id: {}) inputed \"{}\" as their city.".format(
        user.name,
        user.id,
        update.message.text,
    ))
    collection = get_users_collection()
    try:
        city_data = get_city_data(update.message.text)
    except GoogleApiError as e:
        logger.error(msg="Exception while handling an update:", exc_info=e)
        update.message.reply_text(
            'К сожалению, я сломался',
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    if len(city_data['results']) == 0:
        update.message.reply_text(
            'К сожалению я не могу понять что это за город такой - "{}". '
            'Попробуйте ввести город еще раз'.format(update.message.text),
        )
        return ConversationStatus.city

    normalized_city = city_data['results'][0]['formatted_address']
    logger.info("User {} (id: {}) normalized city: \"{}\".".format(
        user.name,
        user.id,
        normalized_city,
    ))
    result = collection.update_one(
        filter=dict(_id=user.id),
        update={'$set': dict(city=normalized_city)}
    )
    assert result.matched_count == 1

    update.message.reply_text(
        'Верно ли я понял, что вы находитесь в "{}"?'.format(normalized_city),
        reply_markup=ReplyKeyboardMarkup(
            [[YES, NO]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )

    return ConversationStatus.city_confirm


def city_confirm(update: Update, context: CallbackContext) -> ConversationStatus | int:
    user = update.effective_user
    if update.message.text == YES:
        logger.info("User {} (id: {}) confirmed the city.".format(user.name, user.id))
        update.message.reply_text(
            'Я сообщу Вам если смогу подобрать подходящую компанию',
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
    elif update.message.text == NO:
        logger.info("User {} (id: {}) did not confirm the city. Asking for city again.".format(user.name, user.id))
        update.message.reply_text(
            'В каком городе Вы находитесь?',
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationStatus.city
    return ConversationStatus.city_confirm


def delete(update: Update, context: CallbackContext) -> ConversationStatus | int:
    user = update.effective_user
    logger.info("User {} (id: {}) decided to delete their data.".format(user.name, user.id))
    collection = get_users_collection()
    collection.delete_one(filter=dict(_id=user.id))
    update.message.reply_text(
        'Я забыл все что вы мне сообщали. Если все же решите найти собеседников напишите /start',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def make_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ConversationStatus.city: [MessageHandler(Filters.text & ~Filters.command, city)],
            ConversationStatus.city_confirm: [MessageHandler(Filters.text & ~Filters.command, city_confirm)],
        },
        fallbacks=[CommandHandler('delete', delete)],
    )
