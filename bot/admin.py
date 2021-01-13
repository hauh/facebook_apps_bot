"""Admin menu."""

from telegram.constants import CHAT_PRIVATE
from telegram.ext import (
	CallbackQueryHandler, CommandHandler, ConversationHandler, Filters,
	MessageHandler
)
from telegram.ext.filters import MessageFilter

from bot import db
from bot.replies import (
	add_acc_btn, add_acc_texts, admin_main_text, back_btn, button, confirm_btn,
	manage_acc_buttons, manage_acc_texts, reply
)


class AdminFilter(MessageFilter):
	"""Filtering out non-private non-admin messages."""

	def filter(self, message):
		return message.chat.type == CHAT_PRIVATE


def admin_main(update, context):
	context.user_data.pop('new_account', None)
	context.user_data.pop('managed_account', None)

	buttons = [add_acc_btn]
	for account_id, login in db.get_accounts():
		buttons.append(button(login, f'manage_{account_id}'))
	buttons.append(back_btn)
	reply(update, context, admin_main_text, buttons)
	return 1


def back_to_admin(update, context):
	admin_main(update, context)
	return -1


def back_to_start(update, context):
	context.bot.restart(update, context)
	return -1


# add account #

def add_account(update, context):
	context.user_data['new_account'] = {}
	reply(update, context, add_acc_texts['ask_login'], [back_btn])
	return 1


def get_login(update, context):
	login = update.effective_message.text
	context.user_data['new_account']['login'] = login
	message = add_acc_texts['ask_password'].format(login)
	reply(update, context, message, [back_btn])
	return 2


def get_password(update, context):
	new_account = context.user_data['new_account']
	new_account['password'] = update.effective_message.text
	message = add_acc_texts['confirm'].format(**new_account)
	reply(update, context, message, [confirm_btn, back_btn])
	return 3


def do_add_account(update, context):
	db.add_account(**context.user_data['new_account'])
	return back_to_admin(update, context)


add_account_conversation = ConversationHandler(
	entry_points=[CallbackQueryHandler(add_account, pattern=r'^add_account$')],
	states={
		1: [MessageHandler(Filters.text, get_login)],
		2: [MessageHandler(Filters.text, get_password)],
		3: [CallbackQueryHandler(do_add_account, pattern=r'^confirm$')],
	},
	fallbacks=[CallbackQueryHandler(back_to_admin, pattern=r'^back$')],
	map_to_parent={-1: 1}
)


# manage account #

def get_managed_account(update, context):
	account_id = int(update.callback_query.data.removeprefix('manage_'))
	context.user_data['managed_account'] = account_id
	return manage_account_menu(update, context)


def manage_account_menu(update, context):
	reply(update, context, manage_acc_texts['main'], manage_acc_buttons)
	return 1


def add_app(update, context):
	reply(update, context, manage_acc_texts['add_app'], [back_btn])
	return 11


def do_add_app(update, context):
	try:
		app_id = int(update.effective_message.text)
	except ValueError:
		reply(update, context, manage_acc_texts['nan'], [back_btn])
		return 11
	db.add_app(app_id, context.user_data['managed_account'])
	return manage_account_menu(update, context)


def remove_app(update, context):
	buttons = []
	for app_id in db.get_apps_for_account(context.user_data['managed_account']):
		buttons.append(button(str(app_id), f'remove_{app_id}'))
	buttons.append(back_btn)
	reply(update, context, manage_acc_texts['remove_app'], buttons)
	return 12


def do_remove_app(update, context):
	app_id = int(update.callback_query.data.removeprefix('remove_'))
	db.remove_app(app_id)
	return manage_account_menu(update, context)


def change_password(update, context):
	reply(update, context, manage_acc_texts['change_pass'], [back_btn])
	return 13


def do_change_password(update, context):
	new_password = update.effective_message.text
	db.change_password(context.user_data['managed_account'], new_password)
	return manage_account_menu(update, context)


def delete_account(update, context):
	message = manage_acc_texts['delete_account']
	reply(update, context, message, [confirm_btn, back_btn])
	return 14


def do_delete_account(update, context):
	db.remove_account(context.user_data.pop('managed_account'))
	admin_main(update, context)
	return -1


manage_account_conversation = ConversationHandler(
	entry_points=[CallbackQueryHandler(get_managed_account, pattern=r'^manage_')],
	states={
		1: [
			CallbackQueryHandler(add_app, pattern=r'^add_app$'),
			CallbackQueryHandler(remove_app, pattern=r'^remove_app$'),
			CallbackQueryHandler(change_password, pattern=r'^change_password$'),
			CallbackQueryHandler(delete_account, pattern=r'^delete_account$'),
			CallbackQueryHandler(back_to_admin, pattern=r'^back$')
		],
		11: [MessageHandler(Filters.text, do_add_app)],
		12: [CallbackQueryHandler(do_remove_app, pattern=r'^remove_')],
		13: [MessageHandler(Filters.text, do_change_password)],
		14: [CallbackQueryHandler(do_delete_account, pattern=r'^confirm$')],
	},
	fallbacks=[CallbackQueryHandler(manage_account_menu, pattern=r'^back$')],
	map_to_parent={-1: 1},
	allow_reentry=True
)


# #####

admin_menu = ConversationHandler(
	entry_points=[CommandHandler('admin', admin_main)],
	states={
		1: [add_account_conversation, manage_account_conversation],
	},
	fallbacks=[CallbackQueryHandler(back_to_start, pattern=r'^back$')],
	allow_reentry=True
)
