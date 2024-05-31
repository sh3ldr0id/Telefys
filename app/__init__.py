from json import loads
from app.database.firebase import initFirebase

import telebot

config = None

with open("config/config.json") as file:
    data = file.read()

config = loads(data)

TOKEN = config["token"]

MAIN_CHANNEL = config["channels"]["main"]
BACKUP_CHANNELS = config["channels"]["backups"]

initFirebase()

bot = telebot.TeleBot(TOKEN)

from app.handlers.commands import create_folder, start, delete
from app.handlers.messages import files, create_folder
from app.handlers.callbacks import open_folder