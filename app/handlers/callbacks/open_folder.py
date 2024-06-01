from app import bot, MAIN_CHANNEL
from app.helpers.constants import OPEN_FOLDER

from telebot import types

from firebase_admin import firestore

from threading import Timer

db = firestore.client()

users_collection = db.collection("users")
files_collection = db.collection("files")
folders_collection = db.collection("folders")

@bot.callback_query_handler(func=lambda x: True)
def answer(callback):
    if callback.message and callback.data.startswith(OPEN_FOLDER):
        messages_to_delete = []

        current_folder_id = callback.data.split("_")[-1]
        current_folder = folders_collection.document(current_folder_id).get()

        user = users_collection.document(str(callback.message.chat.id))
        user.update({"current": current_folder_id})

        viewing_message_id = bot.send_message(callback.message.chat.id, f"Viewing '{current_folder.get('name')}'").message_id
        messages_to_delete.append(viewing_message_id)

        files = current_folder.get("files")
        folders = current_folder.get("folders")

        for fileId in files:
            file = files_collection.document(fileId).get()
            message_id = file.get("main")

            forwarded_message_id = bot.forward_message(callback.message.chat.id, MAIN_CHANNEL, message_id).message_id
            messages_to_delete.append(forwarded_message_id)

        for folderId in folders:
            folder = folders_collection.document(folderId).get()

            folder_name = folder.get("name")
            folder_date = folder.get("date")

            markup = types.InlineKeyboardMarkup(row_width=2)

            open_folder = types.InlineKeyboardButton("Open", callback_data=OPEN_FOLDER+folderId)
            markup.add(open_folder)

            folder_message_id = bot.send_message(callback.message.chat.id, f"📁 {folder_name} \n📅 {folder_date.strftime('%Y-%m-%d %H:%M:%S')}", reply_markup=markup).message_id
            messages_to_delete.append(folder_message_id)

        end_message_id = bot.send_message(callback.message.chat.id, "That's it. :)").message_id
        messages_to_delete.append(end_message_id)

        Timer(60*5, bot.delete_messages, args=(callback.message.chat.id, messages_to_delete)).start()