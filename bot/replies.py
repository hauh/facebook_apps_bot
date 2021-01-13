"""Bot's replies."""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, TelegramError


def reply(update, context, text, buttons=None, answer=None):
	"""Reply to user, answer callback query, and clean chat."""
	keyboard = InlineKeyboardMarkup(buttons) if buttons else None
	message = update.effective_chat.send_message(text, reply_markup=keyboard)
	if update.callback_query:
		update.callback_query.answer(text=answer)
		previous_message = update.callback_query.message
	else:
		previous_message = context.user_data.pop('previous_message', None)
	if previous_message:
		try:
			previous_message.delete()
		except TelegramError as err:
			logging.warning("Chat error - %s", err)
	context.user_data['previous_message'] = message


def button(text, callback_data):
	return [InlineKeyboardButton(text, callback_data=callback_data)]


# main menu #
main_menu_text = "Главное меню."
connect_ad_account_btn = button("Подключить аккаунт", 'connect_ad_account')

# admin menu #
admin_main_text = "Управление аккаунтами."
back_btn = button("Назад", 'back')
confirm_btn = button("Подтвердить", 'confirm')

# admin add account menu #
add_acc_texts = {
	'ask_login': "Введите логин.",
	'ask_password': "{}\n\nВведите пароль.",
	'confirm': "{login}\n{password}\n\nДобавить аккаунт?",
}
add_acc_btn = button("Добавить аккаунт", 'add_account')

# admin manage accounts menu #
manage_acc_texts = {
	'main': "Управление аккаунтом.",
	'add_app': "Введите ID приложения.",
	'nan': "ID приложения должно быть числом.",
	'remove_app': "Выберите приложение, которое нужно удалить.",
	'change_pass': "Введите новый пароль.",
	'delete_account': "Удалить аккаунт? Все его приложения также будут удалены.",
}
manage_acc_buttons = [
	button("Добавить приложение", 'add_app'),
	button("Удалить приложение", 'remove_app'),
	button("Сменить пароль", 'change_password'),
	button("Удалить аккаунт", 'delete_account'),
	back_btn
]
