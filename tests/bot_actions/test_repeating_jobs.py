# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import pytz
from time import sleep
from telegram.utils.helpers import DEFAULT_NONE

import pytest
from unittest.mock import Mock

from app.bot_actions.repeating_jobs import try_to_group_people


class TestTryToGroupPeopleWOBot:
    @pytest.fixture(autouse=True)
    def _setup(self, mongo_mock):
        self.mongo_mock = mongo_mock

    def test_does_nothing_if_no_users(self):
        self.mongo_mock.users.find.return_value = []
        context_mock = Mock()
        try_to_group_people(context_mock)
        assert self.mongo_mock.users.find.call_count == 1
        assert self.mongo_mock.users.find.call_args.kwargs == dict(filter={})
        assert context_mock.bot.send_message.call_count == 0

    def test_does_nothing_if_users_does_not_have_cities(self):
        self.mongo_mock.users.find.return_value = [
            dict(),
            dict(),
            dict(),
        ]
        context_mock = Mock()
        try_to_group_people(context_mock)
        assert self.mongo_mock.users.find.call_count == 1
        assert self.mongo_mock.users.find.call_args.kwargs == dict(filter={})
        assert context_mock.bot.send_message.call_count == 0

    @pytest.mark.xfail  # it should fail for now
    def test_does_nothing_if_only_one_user(self):
        self.mongo_mock.users.find.return_value = [
            dict(
                _id=1111,
                name='name',
                city='Moscow',
                timezone='Europe/Moscow',
                dates=[
                    (datetime.now(tz=pytz.timezone('Europe/Moscow')) + timedelta(days=1)).date().isoformat(),
                ],
            ),
        ]
        context_mock = Mock()
        try_to_group_people(context_mock)
        assert self.mongo_mock.users.find.call_count == 1
        assert self.mongo_mock.users.find.call_args.kwargs == dict(filter={})
        assert context_mock.bot.send_message.call_count == 0

    def test_groups_2_users(self):
        tomorrow_iso = (datetime.now(tz=pytz.timezone('Europe/Moscow')) + timedelta(days=1)).date().isoformat()
        self.mongo_mock.users.find.return_value = [
            dict(
                _id=1111,
                name='@name',
                city='Moscow',
                timezone='Europe/Moscow',
                dates=[tomorrow_iso],
            ),
            dict(
                _id=2222,
                name='@name2',
                city='Moscow',
                timezone='Europe/Moscow',
                dates=[tomorrow_iso],
            ),
        ]
        context_mock = Mock()
        try_to_group_people(context_mock)
        assert self.mongo_mock.users.find.call_count == 1
        assert self.mongo_mock.users.find.call_args.kwargs == dict(filter={})
        assert context_mock.bot.send_message.call_count == 2
        assert context_mock.bot.send_message.call_args_list[0].kwargs == dict(
            chat_id=1111,
            text='Я подобрал группу для встречи в "Moscow" завтра, {}: @name, @name2'.format(tomorrow_iso),
        )
        assert context_mock.bot.send_message.call_args_list[1].kwargs == dict(
            chat_id=2222,
            text='Я подобрал группу для встречи в "Moscow" завтра, {}: @name, @name2'.format(tomorrow_iso),
        )


class TestTryToGroupPeopleWBot:
    @pytest.fixture(autouse=True)
    def _setup(self, mongo_mock, updater):
        self.mongo_mock = mongo_mock
        self.updater = updater

    def test_try_to_group_people(self):
        tomorrow_iso = (datetime.now(tz=pytz.timezone('Europe/Moscow')) + timedelta(days=1)).date().isoformat()
        self.mongo_mock.users.find.return_value = [
            dict(
                _id=1111,
                name='@name',
                city='Moscow',
                timezone='Europe/Moscow',
                dates=[tomorrow_iso],
            ),
            dict(
                _id=2222,
                name='@name2',
                city='Moscow',
                timezone='Europe/Moscow',
                dates=[tomorrow_iso],
            ),
        ]
        sleep(2)
        assert len(self.updater.bot.sent_messages) == 2
        assert self.updater.bot.sent_messages[0] == dict(
            allow_sending_without_reply=DEFAULT_NONE,
            chat_id=1111,
            disable_notification=DEFAULT_NONE,
            disable_web_page_preview=DEFAULT_NONE,
            parse_mode=DEFAULT_NONE,
            text='Я подобрал группу для встречи в "Moscow" завтра, {}: @name, @name2'.format(tomorrow_iso),
        )
        assert self.updater.bot.sent_messages[1] == dict(
            allow_sending_without_reply=DEFAULT_NONE,
            chat_id=2222,
            disable_notification=DEFAULT_NONE,
            disable_web_page_preview=DEFAULT_NONE,
            parse_mode=DEFAULT_NONE,
            text='Я подобрал группу для встречи в "Moscow" завтра, {}: @name, @name2'.format(tomorrow_iso),
        )
