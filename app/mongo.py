# -*- coding: utf-8 -*-
from pymongo import MongoClient

from . import settings

__mongo_client = None


def get_mongo_db():
    global __mongo_client
    if __mongo_client is None:
        __mongo_client = MongoClient(settings.MONGODB_CONNECTION_STRING)

    return __mongo_client[settings.MONGODB_DB_NAME]
