"""Facebook Apps Bot."""

import logging

from telegram import InlineKeyboardMarkup, TelegramError
from telegram.ext import CommandHandler

from bot import updater


def reply(update, text, buttons=None, answer=None):
	"""Reply to user, answer callback query, and clean chat."""
	keyboard = InlineKeyboardMarkup(buttons) if buttons else None
	update.effective_chat.send_message(text, reply_markup=keyboard)
	if update.callback_query:
		try:
			update.callback_query.answer(text=answer)
			update.callback_query.delete_message()
		except TelegramError as err:
			logging.warning("Chat error - %s", err)


def start(update, context):
	context.bot.reply("START")


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
	setattr(updater.bot, 'reply', reply)
	setattr(updater.bot, 'restart', start)

	dispatcher = updater.dispatcher
	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_error_handler(error)

	updater.start_polling()
	logging.info("Bot started!")

	updater.idle()
	logging.info("Turned off.")


if __name__ == "__main__":
	main()
