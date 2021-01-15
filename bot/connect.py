"""Connect user's accounts to app."""

import logging

from telegram.ext import (
	CallbackQueryHandler, ConversationHandler, Filters, MessageHandler
)

from bot import db, facebook
from bot.replies import back_btn, confirm_btn
from bot.replies import connect_texts as texts
from bot.replies import reply


def start(update, context):
	reply(update, context, texts['app_id'], [back_btn])
	return 1


def get_app_id(update, context):
	try:
		app_id = int(update.effective_message.text)
	except ValueError:
		reply(update, context, texts['nan'], [back_btn])
		return 1
	if not (app_account := db.get_app_account(app_id)):
		reply(update, context, texts['app_not_found'], [back_btn])
		return 1
	context.user_data['connect_accounts'] = {
		'app_id': app_id,
		'app_account': app_account,
		'ad_accounts': set()
	}
	reply(update, context, texts['ad_account'].format(app_id), [back_btn])
	return 2


def get_ad_account_id(update, context):
	try:
		ad_account_id = int(update.effective_message.text)
	except ValueError:
		reply(update, context, texts['nan'], [back_btn])
		return 2
	connect_data = context.user_data['connect_accounts']
	connect_data['ad_accounts'].add(ad_account_id)
	message_text = texts['finish'].format(
		connect_data['app_id'],
		'\n'.join(str(ad_acc_id) for ad_acc_id in connect_data['ad_accounts'])
	)
	reply(update, context, message_text, [confirm_btn, back_btn])
	return 3


def connect(update, context):
	update.effective_message.edit_text(texts['working'], reply_markup=None)
	connect_data = context.user_data.pop('connect_accounts')
	app_id, ad_accounts = connect_data['app_id'], connect_data['ad_accounts']
	try:
		connected_accounts = facebook.update_app(**connect_data)
	except Exception as err:  # pylint: disable=broad-except
		message_text = texts['result_fail']
		logging.error("Ad accounts connection error: %s", err)
	else:
		not_connected = ad_accounts.difference(connected_accounts)
		count = len(ad_accounts) - len(not_connected)
		message_text = texts['result_success'].format(app_id, count)
		if not_connected:
			message_text += texts['result_partial'].format(
				'\n'.join(str(missing_id) for missing_id in not_connected)
			)
		if count:
			logging.info("New ad accounts (%s) connected to app %s", count, app_id)
	reply(update, context, message_text, [back_btn])
	return 1


def back(update, context):
	context.bot.restart(update, context)
	return -1


connect_conversation = ConversationHandler(
	entry_points=[CallbackQueryHandler(start, pattern=r'^connect_ad_account$')],
	states={
		1: [MessageHandler(Filters.text, get_app_id)],
		2: [MessageHandler(Filters.text, get_ad_account_id)],
		3: [
			CallbackQueryHandler(connect, pattern=r'^confirm$'),
			MessageHandler(Filters.text, get_ad_account_id),
		]
	},
	fallbacks=[CallbackQueryHandler(back, pattern=r'^back$')],
	allow_reentry=True
)
