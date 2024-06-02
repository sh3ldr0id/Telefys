from app import bot, MAIN_CHANNEL, BACKUP_CHANNEL

from firebase_admin import firestore

from datetime import datetime

from threading import Timer

db = firestore.client()

users_collection = db.collection("users")
files_collection = db.collection("files")
folders_collection = db.collection("folders")

@bot.message_handler()
def create_folder(message):
    if message.text == "Home":
        end_message_id = bot.reply_to(message, "Please choose a different name.").message_id
        Timer(10, bot.delete_messages, args=(message.chat.id, [message.message_id, end_message_id])).start()
        
        return 
    
    user_doc = users_collection.document(str(message.chat.id))
    user = user_doc.get()

    listening = user.get("listening")

    if listening == "folder_name":
        current_folder_id = user.get("current")
        current_folder = folders_collection.document(current_folder_id)

        folder_id = folders_collection.add({
            "owner": str(message.chat.id),
            "previous": current_folder_id,
            "name": message.text,
            "files": [],
            "folders": [],
            "date": datetime.now(),
            "shared": False
        })[1].id

        current_folder.update({"folders": firestore.ArrayUnion([folder_id])})

        user_doc.update({"listening": None, "question": None})

        question_id = user.get("question")

        confirm_id = bot.reply_to(message, f"Done! Created '{message.text}' in '{current_folder.get().get('name')}'").message_id

        Timer(10, bot.delete_messages, args=(message.chat.id, [question_id, message.message_id, confirm_id])).start()