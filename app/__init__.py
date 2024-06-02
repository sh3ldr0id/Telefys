from json import loads
from app.database.firebase import initFirebase

import telebot

config = None

with open("config/config.json") as file:
    data = file.read()

config = loads(data)

TOKEN = config["token"]

MAIN_CHANNEL = config["channels"]["main"]
BACKUP_CHANNEL = config["channels"]["backup"]

initFirebase()

bot = telebot.TeleBot(TOKEN)

from app.handlers.commands import start, create_folder, list_dir, back
from app.handlers.messages import files, create_folder
from app.handlers import callbacks