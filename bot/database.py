"""Database manager."""

import logging
import sqlite3
from threading import Lock


class Database:
	"""SQLite3 database manager."""

	def __init__(self, db_name):
		self.connection = sqlite3.connect(
			db_name,
			check_same_thread=False,
			detect_types=sqlite3.PARSE_DECLTYPES
		)
		self.lock = Lock()
		self.transact("PRAGMA foreign_keys = 1")
		self.transact(
			"""
			CREATE TABLE if not exists 'accounts' (
				'id' INTEGER primary key,
				'login' TEXT not null,
				'password' TEXT not null
			)
			"""
		)
		self.transact(
			"""
			CREATE TABLE if not exists 'apps' (
				'id' INTEGER primary key,
				'account' INTEGER references accounts ('id') on delete CASCADE
			)
			"""
		)
		logging.info("Database connected.")

	def __del__(self):
		self.connection.close()

	def transact(self, query, params=()):
		with self.lock:
			try:
				with self.connection as connection:
					return connection.execute(query, params)
			except sqlite3.DatabaseError as err:
				logging.error("Database error - %s", err)
				raise

	def add_account(self, login, password):
		self.transact(
			"INSERT INTO accounts (login, password) values (?, ?)",
			(login, password)
		)
		logging.info("New account (%s) added.", login)

	def add_app(self, app_id, account_id):
		self.transact(
			"INSERT INTO apps (id, account) values (?, ?)",
			(app_id, account_id)
		)
		logging.info("New app (%s) added.", app_id)

	def get_accounts(self):
		return self.transact("SELECT id, login FROM accounts").fetchall()

	def get_account_for_app(self, app_id):
		return self.transact(
			"""
			SELECT login, password FROM accounts WHERE id IN
			(SELECT account FROM apps WHERE id = ?)
			""",
			(app_id,)
		).fetchone()

	def get_apps_for_account(self, account_id):
		cur = self.transact("SELECT id FROM apps WHERE account = ?", (account_id,))
		cur.row_factory = lambda _, row: row[0]
		return cur.fetchall()

	def change_password(self, account_id, new_password):
		self.transact(
			"UPDATE accounts SET password = ? WHERE id = ?",
			(new_password, account_id,)
		)

	def remove_account(self, account_id):
		self.transact("DELETE FROM accounts WHERE id = ?", (account_id,))
		logging.info("Account (%s) deleted.", account_id)

	def remove_app(self, app_id):
		self.transact("DELETE FROM apps WHERE id = ?", (app_id,))
		logging.info("App (%s) deleted.", app_id)

	def _test(self):
		self.add_account("user", "pass")
		self.add_account("user2", "pass2")
		assert len(self.get_accounts()) == 2
		self.add_app(111, 1)
		self.add_app(222, 1)
		self.add_app(333, 2)
		assert len(self.get_apps_for_account(2)) == 1
		assert len(self.get_apps_for_account(1)) == 2
		account = self.get_account_for_app(111)
		assert account is not None
		assert len(account) == 2
		assert account[0] == "user"
		assert account[1] == "pass"
		self.change_password(1, "new_pass")
		assert self.get_account_for_app(111)[1] == "new_pass"
		self.remove_app(111)
		self.remove_app(222)
		self.remove_app(333)
		assert len(self.get_apps_for_account(1)) == 0
		assert len(self.get_apps_for_account(2)) == 0
		self.remove_account(1)
		self.remove_account(2)
		assert len(self.get_accounts()) == 0
