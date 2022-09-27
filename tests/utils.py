# -*- coding: utf-8 -*-
from datetime import datetime
import pytz
from time import sleep
from typing import Union

from telegram.ext.extbot import ExtBot
from telegram.utils.helpers import DEFAULT_NONE
from telegram.utils.types import JSONDict, ODVInput


BOT_SHORT_DATA = {
    'id': 1111111,
    'is_bot': True,
    'first_name': 'test_bot',
    'username': 'test_bot',
}
BOT_LONG_DATA = dict(
    BOT_SHORT_DATA,
    can_join_groups=True,
    can_read_all_group_messages=False,
    supports_inline_queries=False,
)
USER_CHAT_DATA = {
    'id': 2222222,
    'first_name': 'Firstname',
    'last_name': 'Lastname',
    'username': 'username',
    'type': 'private',
}
USER_FROM_DATA = dict(
    {k: USER_CHAT_DATA[k] for k in ['id', 'first_name', 'last_name', 'username']},
    is_bot=False,
    language_code='ru',
)


LAST_MESSAGE_ID = 0


def get_next_message_id():
    global LAST_MESSAGE_ID
    LAST_MESSAGE_ID += 1
    return LAST_MESSAGE_ID


def make_send_message_response(data: dict):
    return {
        'message_id': get_next_message_id(),
        'from': BOT_SHORT_DATA,
        'chat': USER_CHAT_DATA,
        'text': data['text'],
        'date': int(datetime.now().timestamp()),
    }


def make_update_with_start():
    return {
        'update_id': 821428760,
        'message': {
            'message_id': get_next_message_id(),
            'from': USER_FROM_DATA,
            'chat': USER_CHAT_DATA,
            'date': 1663351421,
            'text': '/start',
            'entities': [{
                'offset': 0,
                'length': 6,
                'type': 'bot_command',
            }],
        },
    }


class TestBot(ExtBot):
    def __init__(self, *args, **kwargs):
        super(TestBot, self).__init__(*args, **kwargs)
        self.sent_messages = []
        self.update_to_send = None

    def _post(
        self,
        endpoint: str,
        data: JSONDict = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[bool, JSONDict, None]:
        if endpoint == 'setMyCommands':
            return True
        elif endpoint == 'getMe':
            return BOT_LONG_DATA
        elif endpoint == 'deleteWebhook':
            return True
        elif endpoint == 'sendMessage':
            self.sent_messages.append(data)
            return make_send_message_response(data)
        elif endpoint == 'getUpdates':
            sleep(0.01)
            result = [] if self.update_to_send is None else [self.update_to_send]
            self.update_to_send = None
            return result
        raise AttributeError('unknown method')


def make_city_data_response(status='OK'):
    return {
        'results': [
            {
                'address_components': [
                    {'long_name': 'Вашингтон', 'short_name': 'Вашингтон', 'types': ['locality', 'political']},
                    {'long_name': 'District of Columbia', 'short_name': 'District of Columbia', 'types': ['administrative_area_level_2', 'political']},
                    {'long_name': 'округ Колумбия', 'short_name': 'DC', 'types': ['administrative_area_level_1', 'political']},
                    {'long_name': 'Соединенные Штаты Америки', 'short_name': 'US', 'types': ['country', 'political']},
                ],
                'formatted_address': 'Вашингтон, округ Колумбия, США',
                'geometry': {
                    'bounds': {'northeast': {'lat': 38.9958641, 'lng': -76.909393}, 'southwest': {'lat': 38.7916449, 'lng': -77.119759}},
                    'location': {'lat': 38.9071923, 'lng': -77.0368707},
                    'location_type': 'APPROXIMATE',
                    'viewport': {'northeast': {'lat': 38.9958641, 'lng': -76.909393}, 'southwest': {'lat': 38.7916449, 'lng': -77.119759}},
                },
                'partial_match': True,
                'place_id': 'ChIJW-T2Wt7Gt4kRKl2I1CJFUsI',
                'types': ['locality', 'political']
            }
        ],
        'status': status,
    }


def make_timezone_for_location_response(status='OK', tz_id='America/New_York', errorMessage=None):
    result = {
        'dstOffset': 0,
        'rawOffset': int(datetime.now(pytz.timezone(tz_id)).utcoffset().total_seconds()),
        'status': status,
        'timeZoneId': tz_id,
        'timeZoneName': 'Eastern Standard Time',
    }
    if errorMessage:
        result['errorMessage'] = errorMessage
    return result
