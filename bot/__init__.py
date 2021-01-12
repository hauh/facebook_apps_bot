"""Project Bot package."""

import logging
import os
import sys

from telegram import ParseMode
from telegram.ext import Defaults

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(funcName)s - %(message)s",
	datefmt="%Y.%m.%d %H:%M:%S"
)

try:
	token = os.environ['TOKEN']
except KeyError:
	logging.critical("'TOKEN' environment variable is required.")
	sys.exit(1)

bot_kwargs = {
	'token': token,
	'defaults': Defaults(parse_mode=ParseMode.MARKDOWN)
}
