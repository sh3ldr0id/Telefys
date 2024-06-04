from app import bot
from app.helpers.delete import deleteMessages

from firebase_admin import firestore

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

            deleteMessages(10, message.chat.id, [message.message_id, end_message_id])

            return

        previous = current_folder.get("previous")

        user_doc.update({"current": previous})

        current_folder = folders_collection.document(previous).get()

        bot.delete_message(message.chat.id, message.message_id)

        end_message_id = bot.send_message(message.chat.id, f"Currently in '{current_folder.get('name')}'").message_id

        deleteMessages(60*2, message.chat.id, end_message_id)