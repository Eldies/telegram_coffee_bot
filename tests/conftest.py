# -*- coding: utf-8 -*-
import pymongo

import mongomock
import pytest
from unittest.mock import Mock


@pytest.fixture(autouse=True)
def log_level(caplog):
    import logging
    caplog.set_level(logging.INFO)


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture()
def settings(monkeypatch):
    monkeypatch.setattr('app.settings.BOT_TOKEN', "3333:token")
    monkeypatch.setattr('app.settings.MONGODB_CONNECTION_STRING', "host:11111")
    monkeypatch.setattr('app.settings.MONGODB_DB_NAME', "db_name")
    monkeypatch.setattr('app.settings.GOOGLE_MAPS_API_KEY', "api_key")


@pytest.fixture(autouse=True)
def mongo_mock(monkeypatch, settings):
    monkeypatch.setattr('app.mongo.__mongo_client', None)
#    monkeypatch.setattr('app.mongo.MongoClient', mongomock.MongoClient)
    with mongomock.patch(servers=(('host', 11111),)):
        yield pymongo.MongoClient('host:11111')['db_name']


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
def updater(monkeypatch, settings):
    import app
    from tests.utils import TestBot
    monkeypatch.setattr('telegram.ext.updater.ExtBot', TestBot)
    updater = app.main()
    yield updater
    updater.stop()
