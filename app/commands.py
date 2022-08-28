# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import CallbackContext

from .mongo import get_users_collection


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
    )
    _id = user.id
    collection = get_users_collection()
    item = collection.find_one(dict(_id=_id))
    if item is None:
        collection.insert_one(dict(_id=_id))
