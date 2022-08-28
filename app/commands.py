# -*- coding: utf-8 -*-
from enum import Enum
import logging

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from .mongo import get_users_collection


logger = logging.getLogger(__name__)


class ConversationStatus(Enum):
    city = 1


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
        'Введите /cancel если передумаете.\n\n'
        'В каком городе Вы находитесь?'.format(user.name),
    )

    return ConversationStatus.city


def city(update: Update, context: CallbackContext) -> ConversationStatus:
    user = update.effective_user
    logger.info("User {} (id: {}) inputed \"{}\" as their city.".format(user.name, user.id, update.message.text))
    collection = get_users_collection()
    result = collection.update_one(
        filter=dict(_id=user.id),
        update={'$set': dict(city=update.message.text)}
    )
    assert result.matched_count == 1

    update.message.reply_text(
        'Я сообщу Вам если смогу подобрать подходящую компанию',
    )

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> ConversationStatus:
    user = update.effective_user
    logger.info("User {} (id: {}) cancelled.".format(user.name, user.id))
    collection = get_users_collection()
    collection.delete_one(filter=dict(_id=user.id))
    update.message.reply_text(
        'Я забыл все что вы мне сообщили. Если все же решите найти собеседников напишите /start',
    )
    return ConversationHandler.END


def make_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ConversationStatus.city: [MessageHandler(Filters.text & ~Filters.command, city)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
