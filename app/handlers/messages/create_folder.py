from app import bot, MAIN_CHANNEL, BACKUP_CHANNELS

from firebase_admin import firestore

from datetime import datetime

db = firestore.client()

users_collection = db.collection("users")
files_collection = db.collection("files")
folders_collection = db.collection("folders")

@bot.message_handler()
def create_file(message):
    user = users_collection.document(str(message.chat.id)).get()

    listening = user.get("listening")

    if listening == "filename":
        folder_id = folders_collection.add({
            "name": message.text,
            "files": [],
            "folders": [],
            "date": datetime.now()
        })[1].id

        current_folder_id = user.get("current")
        current_folder = folders_collection.document(current_folder_id)

        current_folder.update({"folders": firestore.ArrayUnion([folder_id])})

        bot.reply_to(message, f"Done! Created '{message.text}' in '{current_folder.get().get('name')}'")