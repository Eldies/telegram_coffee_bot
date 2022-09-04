# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import (
    datetime,
    timedelta,
)
import logging
import pytz

from telegram.ext import (
    CallbackContext,

)

from app.mongo import get_users_collection


logger = logging.getLogger(__name__)


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
