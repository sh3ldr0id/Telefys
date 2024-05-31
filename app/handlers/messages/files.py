from app import bot, MAIN_CHANNEL, BACKUP_CHANNELS

from telebot import types

from firebase_admin import firestore

from datetime import datetime
from uuid import uuid4

db = firestore.client()

users_collection = db.collection("users")
files_collection = db.collection("files")
folders_collection = db.collection("folders")

ALLOWED_FILES = ['document', 'photo', 'video', 'audio', 'voice']

@bot.message_handler(content_types=ALLOWED_FILES)
def upload_files(message):
    user = users_collection.document(str(message.chat.id)).get()

    if user.exists:
        if message.content_type != "document":
            bot.send_message(message.chat.id, "Please send these as documents to save.")

        file_name = message.document.file_name
                
        main_message_id = bot.forward_message(MAIN_CHANNEL, message.chat.id, message.message_id).message_id
        backup_message_ids = []

        for BACKUP_CHANNEL in BACKUP_CHANNELS:
            backup_message_id = bot.forward_message(BACKUP_CHANNEL, message.chat.id, message.message_id).message_id

            backup_message_ids.append(backup_message_id)

        file_id = files_collection.add({
            "owner": str(message.chat.id),
            "name": file_name,
            "date": datetime.now(),
            "main": main_message_id,
            "backup": backup_message_id
        })[1].id

        current_folder = user.get("current")

        folders_collection.document(current_folder).update({"files": firestore.ArrayUnion([file_id])})

        bot.reply_to(message, "File saved successfully!")

    else:
        bot.reply_to(message, "Please type /start first!")