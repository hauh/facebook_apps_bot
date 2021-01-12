"""Project Bot."""

import logging
import sys

from telegram.error import TelegramError
from telegram.ext import Filters, MessageHandler, Updater

from bot import bot_kwargs


def error(update, context):
	error_info = f"{context.error.__class__.__name__}: {context.error}"
	if not update or not update.effective_user:
		logging.error("Bot %s", error_info)
	else:
		try:
			update.effective_message.delete()
		except (AttributeError, TelegramError):
			pass
		user = update.effective_user.username or update.effective_user.id
		logging.warning("User '%s' %s", user, error_info)


def echo(update, _context):
	update.effective_chat.send_message(update.effective_message.text)


def main():
	try:
		updater = Updater(**bot_kwargs)
	except TelegramError as err:
		logging.critical("Telegram connection error: %s", err)
		sys.exit(1)

	dispatcher = updater.dispatcher
	dispatcher.add_handler(MessageHandler(Filters.text, echo))
	dispatcher.add_error_handler(error)

	updater.start_polling()
	logging.info("Bot started!")

	updater.idle()
	logging.info("Turned off.")


if __name__ == "__main__":
	main()
