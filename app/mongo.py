# -*- coding: utf-8 -*-
import pymongo

from . import settings

from app.utils import Singleton


class Mongo(metaclass=Singleton):
    def __init__(self):
        self._client = pymongo.MongoClient(settings.MONGODB_CONNECTION_STRING)

    @property
    def db(self):
        return self._client[settings.MONGODB_DB_NAME]


def get_users_collection():
    return Mongo().db.users
