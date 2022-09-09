# -*- coding: utf-8 -*-
import pytest
from unittest.mock import Mock, MagicMock

from telegram.utils.request import Request


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "3333:token")
    monkeypatch.setenv("MONGODB_CONNECTION_STRING", "conn_str")
    monkeypatch.setenv("MONGODB_DB_NAME", "db_name")
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "api_key")


@pytest.fixture(autouse=True)
def mongo_mock(monkeypatch):
    mongo_mock = MagicMock()
    monkeypatch.setattr('app.mongo.get_mongo_db', mongo_mock)
    return mongo_mock


@pytest.fixture(autouse=True)
def google_maps_city_data(monkeypatch):
    city_data_mock = Mock
    monkeypatch.setattr('app.google_maps.get_city_data', city_data_mock)
    return city_data_mock


@pytest.fixture(autouse=True)
def google_maps_timezone_for_location(monkeypatch):
    timezone_for_location_mock = Mock
    monkeypatch.setattr('app.google_maps.get_timezone_for_location', timezone_for_location_mock)
    return timezone_for_location_mock


@pytest.fixture()
def run_main(monkeypatch, env_vars):
    import app
    from tests.utils import TestBot
    updater = app.main(bot=TestBot(
        token='3333:token',
        request=Request(),
    ))
    updater.job_queue.stop()
    yield
    updater.stop()
