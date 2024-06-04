from app import bot, MAIN_CHANNEL
from app.helpers.name import fetchName
from app.helpers.constants import OPEN_FOLDER, DELETE, FILE, FOLDER
from app.helpers.delete import deleteMessages

from telebot import types

from firebase_admin import firestore

from datetime import datetime

db = firestore.client()

users_collection = db.collection("users")
files_collection = db.collection("files")
folders_collection = db.collection("folders")

@bot.message_handler(commands=["start"])
def start(message):    
    messages_to_delete = []

    messages_to_delete.append(message.message_id)

    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)

    create = types.InlineKeyboardButton("/create")
    list_dir = types.InlineKeyboardButton("/list")
    back = types.InlineKeyboardButton("/back")

    markup.add(create, list_dir, back)

    bot.send_message(
        message.chat.id, 
        f"Heyyy {fetchName(message.chat.id)}! \nWelcome to Telegram File System (Telefys) \nby sh3ldr0id.", 
        reply_markup=markup
    ).message_id

    user = users_collection.document(str(message.chat.id)).get()

    if user.exists:
        home_id = user.get("home")

        users_collection.document(str(message.chat.id)).update({"current": home_id})

        viewing_message_id = bot.send_message(message.chat.id, f"Viewing 'Home'").message_id
        messages_to_delete.append(viewing_message_id)

        home_folder = folders_collection.document(home_id).get()

        files = home_folder.get("files")
        folders = home_folder.get("folders")

        for fileId in files:
            file = files_collection.document(fileId).get()

            file_name = file.get("name")
            file_date = file.get("date")

            message_id = file.get("main")

            forwarded_message = bot.forward_message(message.chat.id, MAIN_CHANNEL, message_id)
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

            folder_info_id = bot.send_message(message.chat.id, f"📁 {folder_name} \n📅 {folder_date.strftime('%Y-%m-%d %H:%M:%S')}", reply_markup=markup).message_id
            messages_to_delete.append(folder_info_id)

        end_message_id = bot.send_message(message.chat.id, "That's it. :)").message_id

        messages_to_delete.append(end_message_id)

    else:
        home_id = folders_collection.add({
            "name": "Home",
            "files": [],
            "folders": [],
            "date": datetime.now()
        })[1].id

        users_collection.document(str(message.chat.id)).set({"home": home_id, "current": home_id})

        bot.send_message(message.chat.id, "Create a new folder or Upload a file to start.")

    deleteMessages(60*2, message.chat.id, messages_to_delete)