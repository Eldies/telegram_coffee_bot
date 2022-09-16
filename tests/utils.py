# -*- coding: utf-8 -*-
from time import sleep
from datetime import datetime
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
