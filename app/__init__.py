# -*- coding: utf-8 -*-
import logging

from telegram.ext import (
    CommandHandler,
    Updater,
)

from app import (
    commands,
    settings,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    updater = Updater(settings.BOT_TOKEN)
    updater.bot.set_my_commands([
        ('/start', 'запускает бот'),
        ('/delete', 'удаляет все данные, которые вы ранее сообщали боту'),
    ])

    dispatcher = updater.dispatcher

    dispatcher.add_handler(commands.make_conversation_handler())
    dispatcher.add_handler(CommandHandler('delete', commands.delete))

    updater.job_queue.run_repeating(commands.try_to_group_people, interval=600, first=10)

    updater.start_polling()
    updater.idle()
