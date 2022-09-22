# -*- coding: utf-8 -*-
from unittest.mock import Mock

from app.mongo import Mongo


def test_fixture_settings(settings):
    mongo = Mongo()
    assert mongo.db.client._topology_settings.seeds == {('host', 11111)}
    assert mongo.db.name == 'db_name'


def test_custom_settings(monkeypatch):
    monkeypatch.setattr('app.settings.MONGODB_CONNECTION_STRING', 'hhhhh:22222')
    monkeypatch.setattr('app.settings.MONGODB_DB_NAME', 'some_name')
    mongo = Mongo()
    assert mongo.db.client._topology_settings.seeds == {('hhhhh', 22222)}
    assert mongo.db.name == 'some_name'


def test_is_singleton(settings, monkeypatch):
    from pymongo import MongoClient
    mongo_client_mock = Mock(wraps=MongoClient)
    monkeypatch.setattr('pymongo.MongoClient', mongo_client_mock)
    assert mongo_client_mock.call_count == 0
    mongo1 = Mongo()
    assert mongo_client_mock.call_count == 1
    mongo2 = Mongo()
    assert mongo_client_mock.call_count == 1
    assert mongo1.db.client is mongo2.db.client
