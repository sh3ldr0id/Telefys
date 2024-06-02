from app import bot, MAIN_CHANNEL, BACKUP_CHANNEL
from app.helpers.constants import DELETE, FILE, FOLDER

from firebase_admin import firestore

from threading import Timer

db = firestore.client()

files_collection = db.collection("files")
folders_collection = db.collection("folders")

def delete_file(file_doc):
    file = file_doc.get()

    main_message_id = file.get("main")
    backup_message_id = file.get("backup")

    file_doc.delete()

    bot.delete_message(MAIN_CHANNEL, main_message_id)
    bot.delete_message(BACKUP_CHANNEL, backup_message_id)

def delete_folder(folder_doc):
    folder = folder_doc.get()

    files = folder.get("files")
    folders = folder.get("folders")

    for fileId in files:
        delete_file(files_collection.document(fileId))

    for folderId in folders:
        delete_folder(files_collection.document(folderId))

    folder_doc.delete()

def delete(callback):
    file_or_folder = callback.data.split("_")[1]
    item_id = callback.data.split("_")[2]

    if file_or_folder == FILE:
        file_doc = files_collection.document(item_id)
        file = file_doc.get()

        previous = file.get("previous")

        owner = file.get("owner")
        shared = file.get("shared")

        if owner == str(callback.message.chat.id) or shared == True or (shared != False and str(callback.message.chat.id) in shared):
            delete_file(file_doc)

            folders_collection.document(previous).update({"files": firestore.ArrayRemove([item_id])}) 
            
            end_message_id = bot.reply_to(callback.message, f"Deleted 📄 {file.get('name')}").message_id
            Timer(10, bot.delete_messages, args=(callback.message.chat.id, [callback.message.message_id, callback.message.reply_to_message.message_id, end_message_id])).start()

        else:
            end_message_id = bot.reply_to(callback.message, f"Sorry, You're not authorized to perform actions on this file.").message_id
            Timer(10, bot.delete_messages, args=(callback.message.chat.id, [callback.message.message_id, end_message_id])).start()

    elif file_or_folder == FOLDER:
        folder_doc = folders_collection.document(item_id)
        folder = file_doc.get()

        previous = file.get("previous")

        owner = folder.get("owner")
        shared = folder.get("shared")

        if owner == callback.message.chat.id or shared == True or (shared != False and callback.message.chat.id in shared):
            delete_folder(folder_doc)

            folders_collection.document(previous).update({"folders": firestore.ArrayRemove([item_id])}) 

            end_message_id = bot.reply_to(callback.message, f"Deleted 📁 {folder.get('name')}").message_id
            Timer(10, bot.delete_messages, args=(callback.message.chat.id, [callback.message.message_id, end_message_id])).start()

        else:
            end_message_id = bot.reply_to(callback.message, f"Sorry, You're not authorized to perform actions on this folder.").message_id
            Timer(10, bot.delete_messages, args=(callback.message.chat.id, [callback.message.message_id, end_message_id])).start()
