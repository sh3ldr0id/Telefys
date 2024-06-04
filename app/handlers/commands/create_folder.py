from app import bot

from firebase_admin import firestore

db = firestore.client()

users_collection = db.collection("users")

@bot.message_handler(commands=["create"])
def create_file(message):    
    user = users_collection.document(str(message.chat.id))

    bot.delete_message(message.chat.id, message.message_id)

    question_id = bot.send_message(message.chat.id, "Sure! I'l create a folder. What do you want to name it?").message_id

    user.update({"listening": "folder_name", "question": question_id})    