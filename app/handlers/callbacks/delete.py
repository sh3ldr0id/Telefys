from app import bot, MAIN_CHANNEL
from app.helpers.constants import DELETE, FILE, FOLDER

from firebase_admin import firestore

from threading import Timer

db = firestore.client()

files_collection = db.collection("files")
folders_collection = db.collection("folders")

@bot.callback_query_handler(func=lambda x: True)
def delete(callback):
    if callback.message and callback.data.startswith(DELETE):
        file_or_folder = callback.data.split("_")[1]
        item_id = callback.data.split("_")[2]

        if file_or_folder == FILE:
            file_doc = files_collection.document(item_id)
            file = file_doc.get()

            owner = file.get("owner")
            shared = file.get("shared")

            main_message_id = file.get("main")
            backups = file.get("backups")

            if owner == str(callback.message.chat.id) or shared == True or (shared != False and str(callback.message.chat.id) in shared):
                file_doc.set({})

                bot.delete_message(MAIN_CHANNEL, main_message_id)

                end_message_id = bot.reply_to(callback.message, f"Deleted 📄 {file.get('name')}").message_id

                Timer(10, bot.delete_messages, args=(callback.message.chat.id, [callback.message.message_id, end_message_id])).start()

            else:
                print(owner)

        elif file_or_folder == FOLDER:
            folder_doc = folders_collection.document(item_id)
            folder = file_doc.get()

            owner = folder.get("owner")
            shared = folder.get("shared")

            if owner == callback.message.chat.id or shared == True or (shared != False and callback.message.chat.id in shared):
                folder_doc.set({})

                end_message_id = bot.reply_to(callback.message, f"Deleted 📁 {folder.get('name')}").message_id

                Timer(10, bot.delete_messages, args=(callback.message.chat.id, [callback.message.message_id, end_message_id])).start()

        else:
            print(file_or_folder)
