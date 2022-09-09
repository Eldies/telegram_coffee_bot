# -*- coding: utf-8 -*-
from time import sleep
from datetime import datetime
from typing import Union

from telegram.ext.extbot import ExtBot
from telegram.utils.helpers import DEFAULT_NONE
from telegram.utils.types import JSONDict, ODVInput


BOT_SHORT_DATA = {
    'id': 5000561895,
    'is_bot': True,
    'first_name': 'eldies_test_bot',
    'username': 'eldies_test_bot',
}
BOT_LONG_DATA = dict(
    BOT_SHORT_DATA,
    can_join_groups=True,
    can_read_all_group_messages=False,
    supports_inline_queries=False,
)
USER_CHAT_DATA = {
    'id': 5000566356,
    'first_name': 'Dlavrukhin',
    'last_name': 'Test',
    'username': 'eldies',
    'type': 'private',
}


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


class TestBot(ExtBot):
    sent_messages = []

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
            sleep(1)
            return []
        raise AttributeError('unknown method')
