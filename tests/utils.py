# -*- coding: utf-8 -*-
from datetime import datetime

from telegram.utils.request import Request
old_post = Request.post


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


def make_post_response(url: str, data: dict):
    method = url.split('/')[-1]
    if method == 'setMyCommands':
        return True
    elif method == 'getMe':
        return BOT_LONG_DATA
    elif method == 'deleteWebhook':
        return True
    elif method == 'sendMessage':
        return make_send_message_response(data)
    elif method == 'getUpdates':
        return []
    raise AttributeError('unknown method')
