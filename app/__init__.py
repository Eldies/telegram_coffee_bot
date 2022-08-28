#!/usr/bin/env python
import logging

from telegram.ext import (
    CommandHandler,
    Filters,
    MessageHandler,
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

    dispatcher.add_handler(CommandHandler("start", commands.start))
    dispatcher.add_handler(CommandHandler("help", commands.help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, commands.echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
