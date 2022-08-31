# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import (
    date,
    datetime,
    timedelta,
)
from enum import Enum
import logging
import pytz
import re

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
from .google_maps import (
    get_city_data,
    get_timezone_for_location,
)
from .mongo import get_users_collection


logger = logging.getLogger(__name__)


class ConversationStatus(Enum):
    city_is_moscow = 4
    city = 1
    city_confirm = 2
    days = 3


YES = 'Да'
NO = 'Нет'

DAY_OF_WEEK = [
    'Понедельник',
    'Вторник',
    'Среда',
    'Четверг',
    'Пятница',
    'Суббота',
    'Воскресенье',
]
FINISH_DATE_CHOOSING = 'Закончить выбор дат'


def make_keyboard_for_dates(update: Update) -> ReplyKeyboardMarkup:
    collection = get_users_collection()
    item = collection.find_one(dict(_id=update.effective_user.id))
    dates_from_db = set(map(lambda d: date.fromisoformat(d), item.get('dates', [])))

    nearest_dates = [
        (datetime.now(tz=pytz.timezone(item['timezone'])) + timedelta(days=shift)).date()
        for shift in range(1, 9)
    ]

    dates_strings = [
        '{is_chosen} {date} ({weekday})'.format(
            is_chosen='☑' if d in dates_from_db else '☐',
            date=d.isoformat(),
            weekday=DAY_OF_WEEK[d.weekday()],
        )
        for d in sorted(dates_from_db | set(nearest_dates))
    ]
    buttons = [
        [FINISH_DATE_CHOOSING]
    ] + [
        dates_strings[i:i + 2]
        for i in range(0, len(dates_strings), 2)
    ]

    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True,
    )


def ensure_user_exists(user):
    collection = get_users_collection()
    item = collection.find_one(dict(_id=user.id))
    if item is None:
        logger.info("User {} (id: {}) started bot.".format(user.name, user.id))
        collection.insert_one(dict(
            _id=user.id,
            name=user.name,
        ))


def track_chats(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    event = update.my_chat_member
    logger.info('my_chat_member event from user {}/{} in chat {}'.format(user.name, user.id, event.chat.id))
    if event.chat.type == event.chat.PRIVATE:
        if event.new_chat_member.status == event.new_chat_member.MEMBER:
            ensure_user_exists(user)
        else:
            logger.info("User {} (id: {}) stopped bot.".format(user.name, user.id))
            get_users_collection().delete_one(filter=dict(_id=user.id))


def start(update: Update, _: CallbackContext) -> ConversationStatus:
    user = update.effective_user
    ensure_user_exists(user)
    logger.info("User {} (id: {}) started conversation.".format(user.name, user.id))

    update.message.reply_text(
        'Привет, {}!\n'
        'Я постараюсь найти группу людей, с которыми Вам удобно встретиться.'
        'Введите /cancel если передумаете.\n\n'
        'Вы находитесь в Москве?'.format(user.name),
        reply_markup=ReplyKeyboardMarkup(
            [[YES, NO]],
            resize_keyboard=True,
        ),
    )

    return ConversationStatus.city_is_moscow


def city_is_moscow(update: Update, _: CallbackContext) -> ConversationStatus | int:
    user = update.effective_user
    collection = get_users_collection()
    if update.message.text == YES:
        try:
            city_data = get_city_data('Москва')
            timezone = get_timezone_for_location(
                latitude=city_data['results'][0]['geometry']['location']['lat'],
                longitude=city_data['results'][0]['geometry']['location']['lng'],
            )
        except GoogleApiError as e:
            logger.error(msg="Exception while handling an update:", exc_info=e)
            update.message.reply_text(
                'К сожалению, я сломался',
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END
        normalized_city = city_data['results'][0]['formatted_address']
        collection.update_one(
            filter=dict(_id=user.id),
            update={'$set': dict(
                city=normalized_city,
                timezone=timezone,
            )}
        )

        logger.info('User {} (id: {}) confirmed the city is "{}".'.format(user.name, user.id, normalized_city))
        update.message.reply_text(
            'Отметьте даты, когда Вам удобно встречаться с людьми. Или просто напишите дату в формате год-месяц-число',
            reply_markup=make_keyboard_for_dates(update),
        )
        return ConversationStatus.days
    elif update.message.text == NO:
        logger.info("User {} (id: {}) did not confirm the city is moscow. Asking for city again.".format(user.name, user.id))
        update.message.reply_text(
            'В каком городе Вы находитесь?',
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationStatus.city
    return ConversationStatus.city_is_moscow


def city(update: Update, _: CallbackContext) -> ConversationStatus | int:
    user = update.effective_user
    logger.info("User {} (id: {}) inputted \"{}\" as their city.".format(
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
            'К сожалению я не могу понять что это за город такой - "{}".\n'
            'Попробуйте ввести город еще раз'.format(update.message.text),
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationStatus.city

    if 'locality' not in city_data['results'][0]['types']:
        update.message.reply_text(
            'Вы находитесь в "{}"? Это не похоже на город.\n'
            'Попробуйте ввести город еще раз'.format(city_data['results'][0]['formatted_address']),
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationStatus.city

    normalized_city = city_data['results'][0]['formatted_address']
    logger.info("User {} (id: {}) normalized city: \"{}\".".format(
        user.name,
        user.id,
        normalized_city,
    ))

    try:
        timezone = get_timezone_for_location(
            latitude=city_data['results'][0]['geometry']['location']['lat'],
            longitude=city_data['results'][0]['geometry']['location']['lng'],
        )
    except GoogleApiError as e:
        logger.error(msg="Exception while handling an update:", exc_info=e)
        update.message.reply_text(
            'К сожалению, я сломался',
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    logger.info("User {} (id: {}) timezone: \"{}\".".format(
        user.name,
        user.id,
        timezone,
    ))
    result = collection.update_one(
        filter=dict(_id=user.id),
        update={'$set': dict(
            city=normalized_city,
            timezone=timezone,
        )}
    )
    assert result.matched_count == 1

    update.message.reply_text(
        'Верно ли я понял, что вы находитесь в "{}"?'.format(normalized_city),
        reply_markup=ReplyKeyboardMarkup(
            [[YES, NO]],
            resize_keyboard=True,
        ),
    )

    return ConversationStatus.city_confirm


def city_confirm(update: Update, _: CallbackContext) -> ConversationStatus | int:
    user = update.effective_user
    if update.message.text == YES:
        logger.info("User {} (id: {}) confirmed the city.".format(user.name, user.id))
        update.message.reply_text(
            'Отметьте даты, когда Вам удобно встречаться с людьми. Или просто напишите дату в формате год-месяц-число',
            reply_markup=make_keyboard_for_dates(update),
        )
        return ConversationStatus.days
    elif update.message.text == NO:
        logger.info("User {} (id: {}) did not confirm the city. Asking for city again.".format(user.name, user.id))
        update.message.reply_text(
            'В каком городе Вы находитесь?',
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationStatus.city
    return ConversationStatus.city_confirm


def days(update: Update, _: CallbackContext) -> ConversationStatus | int:
    if update.message.text == FINISH_DATE_CHOOSING:
        update.message.reply_text(
            'Я сообщу Вам если смогу подобрать подходящую компанию, накануне встречи',
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', update.message.text)
    if match is None:
        update.message.reply_text(
            'Не могу разобрать дату',
            reply_markup=make_keyboard_for_dates(update),
        )
        return ConversationStatus.days

    date_string = date(year=int(match.group(1)), month=int(match.group(2)), day=int(match.group(3))).isoformat()

    collection = get_users_collection()
    item = collection.find_one(dict(_id=update.effective_user.id))
    dates_from_db = set(item.get('dates', []))
    new_dates = dates_from_db ^ {date_string}

    collection.update_one(
        filter=dict(_id=update.effective_user.id),
        update={'$set': dict(
            dates=sorted(new_dates),
        )}
    )
    update.message.reply_text(
        'Записал, что Вы {}готовы встретиться {}'.format(
            '' if date_string in new_dates else 'НЕ ',
            date_string,
        ),
        reply_markup=make_keyboard_for_dates(update),
    )
    return ConversationStatus.days


def cancel(update: Update, _: CallbackContext) -> ConversationStatus | int:
    user = update.effective_user
    logger.info("User {} (id: {}) cancelled conversation.".format(user.name, user.id))
    collection = get_users_collection()
    collection.update_one(
        filter=dict(_id=user.id),
        update={'$set': dict(
            city=None,
            timezone=None,
            dates=[],
        )}
    )
    update.message.reply_text(
        'Я забыл все что вы мне сообщали. Если все же решите найти собеседников напишите /start',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def make_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ConversationStatus.city_is_moscow: [MessageHandler(Filters.text & ~Filters.command, city_is_moscow)],
            ConversationStatus.city: [MessageHandler(Filters.text & ~Filters.command, city)],
            ConversationStatus.city_confirm: [MessageHandler(Filters.text & ~Filters.command, city_confirm)],
            ConversationStatus.days: [MessageHandler(Filters.text & ~Filters.command, days)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )


def try_to_group_people(context: CallbackContext):
    collection = get_users_collection()

    city_to_users = defaultdict(list)
    for user in collection.find({}):
        if not user.get('city'):
            continue
        city_to_users[user['city']].append(user)

    for city in city_to_users:
        users = city_to_users[city]
        tomorrow = (datetime.now(tz=pytz.timezone(users[0]['timezone'])) + timedelta(days=1)).date().isoformat()
        users = [user for user in users if tomorrow in user.get('dates', [])]
        for user in users:
            context.bot.send_message(
                chat_id=user['_id'],
                text='Я подобрал группу для встречи в "{city}" завтра, {date}: {names}'.format(
                    city=city,
                    date=tomorrow,
                    names=', '.join(user['name'] for user in users)
                ),
            )
