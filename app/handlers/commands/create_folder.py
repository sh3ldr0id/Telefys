from app import bot

from firebase_admin import firestore

db = firestore.client()

users_collection = db.collection("users")

@bot.message_handler(commands=["create"])
def create_file(message):    
    user = users_collection.document(str(message.chat.id))

    user.update({"listening": "filename"})

    bot.reply_to(message, "Sure! I'l create a folder. What do you want to name it?")