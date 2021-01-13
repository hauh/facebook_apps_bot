"""Facebook Apps Bot."""

import logging

from telegram import TelegramError
from telegram.ext import CommandHandler, Filters, MessageHandler

from bot import updater
from bot.admin import admin_menu
from bot.replies import connect_ad_account_btn, main_menu_text, reply


def start(update, context):
	reply(update, context, main_menu_text, [connect_ad_account_btn])


def clean(update, _context):
	try:
		update.effective_message.delete()
	except TelegramError:
		pass


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


def main():
	setattr(updater.bot, 'restart', start)

	dispatcher = updater.dispatcher
	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_handler(admin_menu)
	dispatcher.add_handler(MessageHandler(Filters.all, clean))
	dispatcher.add_error_handler(error)

	updater.start_polling()
	logging.info("Bot started!")

	updater.idle()
	logging.info("Turned off.")


if __name__ == "__main__":
	main()
