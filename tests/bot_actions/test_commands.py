# -*- coding: utf-8 -*-
import json
import logging
from time import sleep

import pytest
from unittest.mock import Mock

from telegram.ext import ConversationHandler
from telegram.utils.helpers import DEFAULT_NONE

from app import (
    commands,
    texts,
)
from app.bot_actions.commands import ConversationStatus

from tests.utils import make_update_with_start


class TestStart:
    @pytest.fixture(autouse=True)
    def _setup(self, mongo_mock):
        self.mongo_mock = mongo_mock

    def test_ok(self):
        self.mongo_mock.users.find_one.return_value = dict(
            _id=1111,
            name='@name',
        )
        update_mock = Mock()
        update_mock.effective_user.id = 2222
        update_mock.effective_user.name = '@name2'

        result = commands.start(update_mock, Mock())

        assert result == ConversationStatus.city_is_moscow
        assert self.mongo_mock.users.find_one.call_count == 1
        assert self.mongo_mock.users.find_one.call_args.kwargs == dict(filter=dict(_id=2222))
        assert self.mongo_mock.users.insert_one.call_count == 0
        assert update_mock.message.reply_text.call_count == 1
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs) == 2
        assert update_mock.message.reply_text.call_args_list[0].kwargs['text'] == texts.START_TEXT.format('@name2')
        assert 'reply_markup' in update_mock.message.reply_text.call_args_list[0].kwargs
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard) == 1
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0]) == 2
        assert update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0][0].text == 'Да'
        assert update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0][1].text == 'Нет'

    def test_no_user_in_mongo_ok(self):
        self.mongo_mock.users.find_one.return_value = None
        update_mock = Mock()
        update_mock.effective_user.id = 2222
        update_mock.effective_user.name = '@name2'

        result = commands.start(update_mock, Mock())

        assert result == ConversationStatus.city_is_moscow
        assert self.mongo_mock.users.find_one.call_count == 1
        assert self.mongo_mock.users.find_one.call_args.kwargs == dict(filter=dict(_id=2222))
        assert self.mongo_mock.users.insert_one.call_count == 1
        assert self.mongo_mock.users.insert_one.call_args.kwargs == dict(document=dict(_id=2222, name='@name2'))
        assert update_mock.message.reply_text.call_count == 1
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs) == 2
        assert update_mock.message.reply_text.call_args_list[0].kwargs['text'] == texts.START_TEXT.format('@name2')
        assert 'reply_markup' in update_mock.message.reply_text.call_args_list[0].kwargs
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard) == 1
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0]) == 2
        assert update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0][0].text == 'Да'
        assert update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0][1].text == 'Нет'


class TestStartWBot:
    @pytest.fixture(autouse=True)
    def _setup(self, mongo_mock, updater, caplog):
        self.mongo_mock = mongo_mock
        self.updater = updater
        self.caplog = caplog
        updater.job_queue.stop()

    def test_ok(self):
        assert len([h for h in self.updater.dispatcher.handlers[0] if isinstance(h, ConversationHandler)]) == 1
        conversation_handler = [h for h in self.updater.dispatcher.handlers[0] if isinstance(h, ConversationHandler)][0]
        assert len(conversation_handler.conversations) == 0
        self.mongo_mock['users'].find_one.return_value = dict(
            _id=1111,
            name='@name',
        )

        self.updater.bot.update_to_send = make_update_with_start()
        sleep(0.1)

        assert len(self.updater.bot.sent_messages) == 1
        sent_message = self.updater.bot.sent_messages[0]
        assert 'reply_markup' in sent_message
        sent_message['reply_markup'] = json.loads(sent_message['reply_markup'])
        assert sent_message == dict(
            allow_sending_without_reply=DEFAULT_NONE,
            chat_id=2222222,
            disable_notification=DEFAULT_NONE,
            disable_web_page_preview=DEFAULT_NONE,
            parse_mode=DEFAULT_NONE,
            text=texts.START_TEXT.format('@username'),
            reply_markup=dict(
                keyboard=[[
                    dict(text='Да'),
                    dict(text='Нет'),
                ]],
                selective=False,
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
        assert len(conversation_handler.conversations) == 1
        assert (2222222, 2222222) in conversation_handler.conversations
        assert conversation_handler.conversations[(2222222, 2222222)] == ConversationStatus.city_is_moscow
        assert [r for r in self.caplog.records if r.levelno >= logging.WARNING] == [], 'Log contains warnings/errors'
