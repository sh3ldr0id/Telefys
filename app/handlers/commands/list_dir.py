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

@bot.message_handler(commands=["list"])
def list_dir(message):    
    user = users_collection.document(str(message.chat.id)).get()

    if user.exists:
        messages_to_delete = []

        current_folder_id = user.get("current")
        current_folder = folders_collection.document(current_folder_id).get()

        viewing_message_id = bot.send_message(message.chat.id, f"Viewing '{current_folder.get('name')}'").message_id
        messages_to_delete.append(viewing_message_id)

        files = current_folder.get("files")
        folders = current_folder.get("folders")

        for fileId in files:
            file = files_collection.document(fileId).get()

            message_id = file.get("main")

            file_name = file.get("name")
            file_date = file.get("date")

            forwarded_message = bot.forward_message(message.chat.id, MAIN_CHANNEL, message_id)
            messages_to_delete.append(forwarded_message.message_id)

            markup = types.InlineKeyboardMarkup(row_width=1)

            delete = types.InlineKeyboardButton("Delete", callback_data=DELETE+FILE+f"_{fileId}")
            markup.add(delete)

            file_info_id = bot.reply_to(forwarded_message, f"📄 {file_name} \n📅 {file_date.strftime('%Y-%m-%d %H:%M:%S')}", reply_markup=markup).message_id
            messages_to_delete.append(file_info_id)

        for folderId in folders:
            folder = folders_collection.document(folderId).get()

            folder_name = folder.get("name")
            folder_date = folder.get("date")

            markup = types.InlineKeyboardMarkup(row_width=2)

            open_folder = types.InlineKeyboardButton("Open", callback_data=OPEN_FOLDER+folderId)
            delete = types.InlineKeyboardButton("Delete", callback_data=DELETE+FOLDER+f"_{folderId}")
            markup.add(open_folder, delete)

            folder_message_id = bot.send_message(message.chat.id, f"📁 {folder_name} \n📅 {folder_date.strftime('%Y-%m-%d %H:%M:%S')}", reply_markup=markup).message_id
            messages_to_delete.append(folder_message_id)

        end_message_id = bot.send_message(message.chat.id, "That's it. :)").message_id
        messages_to_delete.append(end_message_id)

        Timer(60*2, bot.delete_messages, args=(message.chat.id, messages_to_delete)).start()

    else:
        bot.reply_to(message, "Please use /start first.")