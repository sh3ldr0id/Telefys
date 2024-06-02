from app import bot, MAIN_CHANNEL
from app.helpers.name import fetchName
from app.helpers.constants import OPEN_FOLDER, DELETE, FILE, FOLDER

from telebot import types

from firebase_admin import firestore

from datetime import datetime
from threading import Timer

db = firestore.client()

users_collection = db.collection("users")
files_collection = db.collection("files")
folders_collection = db.collection("folders")

@bot.message_handler(commands=["back"])
def back(message):    
    user_doc = users_collection.document(str(message.chat.id))
    user = user_doc.get()

    if user.exists:
        current_folder_id = user.get("current")
        current_folder = folders_collection.document(current_folder_id).get()

        if current_folder.get('name') == "Home":
            end_message_id = bot.reply_to(message, "You're already at the root folder.").message_id

            Timer(10, bot.delete_messages, args=(message.chat.id, [message.message_id, end_message_id])).start()

        previous = current_folder.get("previous")

        user_doc.update({"current": previous})

        current_folder = folders_collection.document(previous).get()

        bot.delete_message(message.chat.id, message.message_id)

        end_message_id = bot.send_message(message.chat.id, f"Currently in '{current_folder.get('name')}'").message_id

        Timer(60*2, bot.delete_message, args=(message.chat.id, end_message_id)).start()