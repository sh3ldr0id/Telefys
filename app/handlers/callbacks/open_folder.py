from app import bot, MAIN_CHANNEL
from app.helpers.constants import OPEN_FOLDER, DELETE, FILE, FOLDER
from app.helpers.delete import deleteMessages

from telebot import types

from firebase_admin import firestore

db = firestore.client()

users_collection = db.collection("users")
files_collection = db.collection("files")
folders_collection = db.collection("folders")

def open_folder(callback):
    messages_to_delete = []

    messages_to_delete.append(callback.message.message_id)

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

        file_name = file.get("name")
        file_date = file.get("date")

        forwarded_message = bot.forward_message(callback.message.chat.id, MAIN_CHANNEL, message_id)
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

        folder_message_id = bot.send_message(callback.message.chat.id, f"🔑 {folderId} \n📁 {folder_name} \n📅 {folder_date.strftime('%Y-%m-%d %H:%M:%S')}", reply_markup=markup).message_id
        messages_to_delete.append(folder_message_id)

    end_message_id = bot.send_message(callback.message.chat.id, "That's it. :)").message_id
    messages_to_delete.append(end_message_id)

    deleteMessages(60*2, callback.message.chat.id, messages_to_delete)