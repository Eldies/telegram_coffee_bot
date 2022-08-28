#!/usr/bin/env python
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

    dispatcher = updater.dispatcher

    dispatcher.add_handler(commands.make_conversation_handler())

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
