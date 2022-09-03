# -*- coding: utf-8 -*-
import logging

from telegram.ext import (
    ChatMemberHandler,
    CommandHandler,
    Updater,
)

from app import (
    commands,
    repeating_jobs,
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
        ('/cancel', 'удаляет все данные, которые вы ранее сообщали боту'),
    ])

    dispatcher = updater.dispatcher

    dispatcher.add_handler(commands.make_conversation_handler())
    dispatcher.add_handler(CommandHandler('cancel', commands.cancel))
    dispatcher.add_handler(ChatMemberHandler(commands.track_chats, ChatMemberHandler.MY_CHAT_MEMBER))

    updater.job_queue.run_repeating(repeating_jobs.try_to_group_people, interval=600, first=10)

    updater.start_polling()
    updater.idle()
