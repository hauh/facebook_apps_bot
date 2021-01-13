"""Facebook Apps Bot package."""

import logging
import os
import sys
from sqlite3 import DatabaseError

from telegram import ParseMode, TelegramError
from telegram.ext import Defaults, Updater

from bot.database import Database

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(funcName)s - %(message)s",
	datefmt="%Y.%m.%d %H:%M:%S"
)

try:
	updater = Updater(
		token=os.environ['TOKEN'],
		defaults=Defaults(parse_mode=ParseMode.MARKDOWN)
	)
except KeyError:
	logging.critical("'TOKEN' environment variable is required.")
	sys.exit(1)
except TelegramError as err:
	logging.critical("Telegram connection error: %s", err)
	sys.exit(1)

try:
	db = Database('data/facebook.db')
except DatabaseError as err:
	logging.critical("Database connection error: %s", err)
	sys.exit(1)
