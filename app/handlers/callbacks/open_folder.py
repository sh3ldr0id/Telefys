from app import bot, MAIN_CHANNEL
from app.helpers.constants import OPEN_FOLDER

from telebot import types

from firebase_admin import firestore

db = firestore.client()

users_collection = db.collection("users")
files_collection = db.collection("files")
folders_collection = db.collection("folders")

@bot.callback_query_handler(func=lambda call : True)
def answer(callback):
    if callback.message and callback.data.startswith(OPEN_FOLDER):
        current_folder_id = callback.data.split("_")[-1]
        current_folder = folders_collection.document(current_folder_id).get()

        user = users_collection.document(str(callback.message.chat.id))
        user.update({"current": current_folder_id})

        bot.send_message(callback.message.chat.id, f"Viewing '{current_folder.get('name')}'")

        files = current_folder.get("files")
        folders = current_folder.get("folders")

        for fileId in files:
            file = files_collection.document(fileId).get()

            file_name = file.get("name")
            file_date = file.get("date")

            message_id = file.get("main")

            forwarded_message = bot.forward_message(callback.message.chat.id, MAIN_CHANNEL, message_id)
            bot.reply_to(forwarded_message, f"📄 {file_name} \n📅 {file_date}")

        for folderId in folders:
            folder = folders_collection.document(folderId).get()

            folder_name = folder.get("name")
            folder_date = folder.get("date")

            markup = types.InlineKeyboardMarkup(row_width=2)

            open_folder = types.InlineKeyboardButton("Open", callback_data=OPEN_FOLDER+folderId)
            markup.add(open_folder)

            bot.send_message(callback.message.chat.id, f"📁 {folder_name} \n📅 {folder_date}", reply_markup=markup)

        bot.send_message(callback.message.chat.id, "That's it. :)")