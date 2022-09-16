# -*- coding: utf-8 -*-
import pytest
from unittest.mock import Mock

from app import (
    commands,
    texts,
)
from app.bot_actions.commands import ConversationStatus


class TestStart:
    @pytest.fixture(autouse=True)
    def _setup(self, mongo_mock):
        self.mongo_mock = mongo_mock

    def test_ok(self):
        self.mongo_mock.return_value['users'].find_one.return_value = dict(
            _id=1111,
            name='@name',
        )
        update_mock = Mock()
        update_mock.effective_user.id = 2222
        update_mock.effective_user.name = '@name2'
        result = commands.start(update_mock, Mock())
        assert result == ConversationStatus.city_is_moscow
        assert self.mongo_mock.call_count == 1
        assert self.mongo_mock.return_value['users'].find_one.call_count == 1
        assert self.mongo_mock.return_value['users'].find_one.call_args.kwargs == dict(filter=dict(_id=2222))
        assert self.mongo_mock.return_value['users'].insert_one.call_count == 0
        assert update_mock.message.reply_text.call_count == 1
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs) == 2
        assert update_mock.message.reply_text.call_args_list[0].kwargs['text'] == texts.START_TEXT.format('@name2')
        assert 'reply_markup' in update_mock.message.reply_text.call_args_list[0].kwargs
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard) == 1
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0]) == 2
        assert update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0][0].text == 'Да'
        assert update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0][1].text == 'Нет'

    def test_no_user_in_mongo_ok(self):
        self.mongo_mock.return_value['users'].find_one.return_value = None
        update_mock = Mock()
        update_mock.effective_user.id = 2222
        update_mock.effective_user.name = '@name2'
        result = commands.start(update_mock, Mock())
        assert result == ConversationStatus.city_is_moscow
        assert self.mongo_mock.call_count == 1
        assert self.mongo_mock.return_value['users'].find_one.call_count == 1
        assert self.mongo_mock.return_value['users'].find_one.call_args.kwargs == dict(filter=dict(_id=2222))
        assert self.mongo_mock.return_value['users'].insert_one.call_count == 1
        assert self.mongo_mock.return_value['users'].insert_one.call_args.kwargs == dict(document=dict(_id=2222, name='@name2'))
        assert update_mock.message.reply_text.call_count == 1
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs) == 2
        assert update_mock.message.reply_text.call_args_list[0].kwargs['text'] == texts.START_TEXT.format('@name2')
        assert 'reply_markup' in update_mock.message.reply_text.call_args_list[0].kwargs
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard) == 1
        assert len(update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0]) == 2
        assert update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0][0].text == 'Да'
        assert update_mock.message.reply_text.call_args_list[0].kwargs['reply_markup'].keyboard[0][1].text == 'Нет'
