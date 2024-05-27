import telebot
from telebot import types

from firebase_admin.credentials import Certificate
from firebase_admin import initialize_app, firestore

from datetime import datetime

# CONSTS
TOKEN = "6606433414:AAFvjx9FmND5f7EZHzaajkoO6SKkit9MhI0"

TARGET_CHANNEL_ID = -1002168833752
BACKUP_CHANNEL_ID =  -1002184815414

ALLOWED_FILES = ['document', 'photo', 'video', 'audio', 'voice']

class cbd:
    WHITELIST = "whitelist"
    WHITELIST_VIEW = "whitelist_view"
    WHITELIST_ADD = "whitelist_add"
    REVOKE = "revoke_"

    EVENTS = "events"
    VIEW = "view"
    CREATE = "create"
    DELETE_EVENT = "delete_event_"
    UPLOAD = "upload_"
    EVENT = "event_"
    DELETE_FILE = "delete_file_"

# Init Bot
bot = telebot.TeleBot(TOKEN)

# Init Database
creds = Certificate("firebase.json")
initialize_app(creds)

db = firestore.client()

users_coll = db.collection("users")
events_coll = db.collection("events")

# Listners
isListening = {
    "whitelist": [],
    "name": [],
    "date": {},
    "files": {}
}

# Helper Funcs
def exists(uid):
    if not exists:
        bot.send_message(int(uid), f"Dear User, \nPlease ask an admin to verify your id ({uid})")
        return False
    
    return True

def isAdmin(uid):
    return "isAdmin" in users_coll.document(uid).get().to_dict().keys()

def fetchName(chat_id):
    try:
        chat = bot.get_chat(chat_id)
        first_name = chat.first_name
        last_name = chat.last_name
        user_name = f"{first_name} {last_name}" if last_name else first_name
        return user_name
    except Exception as e:
        print(f"Error fetching user name: {e}")
        return None

# Custom Handlers
#(Whitelist)
def handle_whitelist(callback):
    uid = str(callback.message.chat.id)

    markup = types.InlineKeyboardMarkup(row_width=2)

    view = types.InlineKeyboardButton("View existing", callback_data=cbd.WHITELIST_VIEW)
    markup.add(view)

    add = types.InlineKeyboardButton("Add a new member", callback_data=cbd.WHITELIST_ADD)
    markup.add(add)

    bot.send_message(int(uid), f"Welcome to the whitelist.\nStart by choosing an option.", reply_markup=markup)

def handle_whitelist_view(callback):
    uid = str(callback.message.chat.id)

    for user in users_coll.get():
        markup = types.InlineKeyboardMarkup(row_width=1)

        revoke = types.InlineKeyboardButton("Revoke access", callback_data=cbd.REVOKE+user.id)
        markup.add(revoke)

        user_uid = user.id
        user = user.to_dict()

        bot.send_message(int(uid), f"{'🪪\n' if 'isAdmin' in user.keys() else ''}👤{fetchName(user_uid)} ({user_uid})\n 👥{fetchName(user['by'])} ({user['by']})", reply_markup=markup)

def handle_whitelist_revoke(callback, user_uid):
    users_coll.document(user_uid).set({})

def handle_whitelist_add(callback):
    global isListening

    uid = str(callback.message.chat.id)

    isListening["whitelist"].append(uid)

    bot.send_message(int(uid), "Please enter the user's uid.")

#(Events)
def handle_events(callback):
    markup = types.InlineKeyboardMarkup(row_width=2)

    create = types.InlineKeyboardButton("Create New", callback_data=cbd.CREATE)
    markup.add(create)

    events = types.InlineKeyboardButton("View", callback_data=cbd.VIEW)
    markup.add(events)

    bot.send_message(callback.message.chat.id, "View one of the existing events \n\nOR\n\nCreate a new event", reply_markup=markup)

def handle_events_view(callback):
    uid = str(callback.message.chat.id)

    events = events_coll.order_by("date").get()

    for event in events:
        if "deleted" in event.to_dict().keys():
            continue

        document = event.id
        event = event.to_dict()

        markup = types.InlineKeyboardMarkup(row_width=1)

        events = types.InlineKeyboardButton("View", callback_data=cbd.EVENT+"1_"+document)
        markup.add(events)

        upload = types.InlineKeyboardButton("Upload", callback_data=cbd.UPLOAD+document)
        markup.add(upload)

        if isAdmin(uid):
            delete = types.InlineKeyboardButton("Delete", callback_data=cbd.DELETE_EVENT+document)
            markup.add(delete)

        bot.send_message(int(uid), f"{event['name']}\n-{event['date'].strftime('%d-%m-%Y')}", reply_markup=markup)

    bot.send_message(int(uid), "That's it. :)")

def handle_events_create(callback):
    global isListening

    uid = str(callback.message.chat.id)

    bot.send_message(int(uid), "Okay. I'l create a new event for you.\n\nWhat do you want to name it?")

    isListening["name"].append(uid)

def handle_events_delete(callback, document):
    uid = str(callback.message.chat.id)

    if not isAdmin(uid):
        bot.send_message(int(uid), "Successfully deleted the event.")
        return 
    
    events_coll.document(document).update({"deleted": True, "deletedBy": uid})
    bot.delete_message(int(uid), callback.message.id)
    bot.send_message(int(uid), "Successfully deleted the event.")    

def handle_events_upload(callback, document):
    global isListening

    uid = str(callback.message.chat.id)

    isListening["files"][uid] = document

    bot.send_message(int(uid), "Please send your files below")

def handle_event_view(callback, document, page):
    uid = callback.message.chat.id

    event = events_coll.document(document).get().to_dict()

    if not event:
        bot.send_message(uid, "There's nothing else to see. :(") 

    files = event["files"]

    for file in files:
        if "deleted" in file.keys():
            files.remove(file)

    start_index = (page - 1) * 10
    end_index = start_index + 10

    page_files = files[start_index:end_index]

    for file in page_files:
        mid = file["mid"]

        message = bot.forward_message(uid, TARGET_CHANNEL_ID, mid)

        markup = types.InlineKeyboardMarkup(row_width=2)

        delete = types.InlineKeyboardButton("Delete", callback_data=cbd.DELETE_FILE+f"{mid}_"+document)
        markup.add(delete)

        bot.reply_to(message, f"By {fetchName(file['by'])} on {file["date"].strftime('%Y-%m-%d %H:%M:%S')}", reply_markup=markup)

    if end_index == len(files) or len(files) == 0:
        bot.send_message(uid, "There's nothing else to see. :(") 

    else:
        markup = types.InlineKeyboardMarkup(row_width=2)

        events = types.InlineKeyboardButton("Next Page", callback_data=cbd.EVENT+f"{page+1}_"+document)
        markup.add(events)

        bot.send_message(uid, f"Page {page} out of {round(len(files)/10)}", reply_markup=markup)

def handle_delete_file(callback, document, mid):
    uid = str(callback.message.chat.id)

    event = events_coll.document(document).get().to_dict()

    if event:
        files = event["files"]

        for index, file in enumerate(files):
            if file["mid"] == mid:
                files[index]["deleted"] = True
                files[index]["deletedBy"] = uid 
                break

        events_coll.document(document).update({"files": files})

        bot.delete_message(int(uid), callback.message.id-1)
        bot.delete_message(int(uid), callback.message.id)

        bot.send_message(uid, "Deletion success")

        return
# Handlers
@bot.message_handler(commands=["start"])
def start(message):
    uid = str(message.chat.id)

    if not exists(uid):
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)

    events = types.InlineKeyboardButton("Events", callback_data=cbd.EVENTS)
    markup.add(events)

    if isAdmin(uid):
        whitelist = types.InlineKeyboardButton("Whitelist", callback_data=cbd.WHITELIST)
        markup.add(whitelist)

    bot.send_message(message.chat.id, "Heyyy! \n\nWelcome to Telegram File System (Telefys) \nby sh3ldr0id. \n\nHow can I help you?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call : True)
def answer(callback):
    uid = str(callback.message.chat.id)

    if not exists(uid):
        return

    if callback.message:
        cb = callback.data

        # Whitelist CRD

        if cb == cbd.WHITELIST and isAdmin(uid):
            handle_whitelist(callback)

        if cb == cbd.WHITELIST_ADD and isAdmin(uid):
            handle_whitelist_add(callback)
            
        if cb == cbd.WHITELIST_VIEW and isAdmin(uid):
            handle_whitelist_view(callback)

        if cb.startswith(cbd.REVOKE) and isAdmin(uid):
            handle_whitelist_revoke(callback, cb.split("_")[-1])

        # Events CRD

        elif cb == cbd.EVENTS:
            handle_events(callback)

        elif cb == cbd.CREATE:
            handle_events_create(callback)

        elif cb == cbd.VIEW:
            handle_events_view(callback)

        elif cb.startswith(cbd.DELETE_EVENT):
            handle_events_delete(callback, cb.split("_")[-1])

        elif cb.startswith(cbd.UPLOAD):
            handle_events_upload(callback, cb.split("_")[-1])

        elif cb.startswith(cbd.EVENT):
            handle_event_view(callback, cb.split("_")[-1], int(cb.split("_")[-2]))

        elif cb.startswith(cbd.DELETE_FILE):
            handle_delete_file(callback, cb.split("_")[-1], int(cb.split("_")[-2]))

@bot.message_handler(func=lambda message: True)
def event_create(message):
    global isListening

    uid = str(message.chat.id)

    if uid in isListening["name"]:
        isListening["date"][uid] = {
            "name": message.text,
            "files": [],
            "by": uid
        }

        isListening["name"].remove(uid)

        bot.send_message(int(uid), "Now, please enter the date of the event. (DDMMYYYY)")

    elif uid in isListening["date"].keys():
        isListening["date"][uid]["date"] = datetime.strptime(message.text, '%d%m%Y')

        events_coll.add(isListening["date"][uid])

        isListening["date"].pop(uid)

        bot.send_message(int(uid), "Done. I have created a new event for you.")

    elif uid in isListening["whitelist"]:
        isListening["whitelist"].remove(uid)

        users_coll.document(message.text).set({
            "by": uid
        })

        bot.reply_to(message, f"{fetchName(message.text)} ({message.text}) whitelisted.")

@bot.message_handler(content_types=ALLOWED_FILES)
def upload_files(message):
    uid = str(message.chat.id)

    if uid not in isListening["files"].keys():
        bot.send_message(int(uid), "Please select an event before sending files.")
        return 
    
    if message.content_type in ALLOWED_FILES:
        mid = bot.forward_message(TARGET_CHANNEL_ID, uid, message.message_id).message_id
        events_coll.document(isListening["files"][uid]).update({"files": firestore.ArrayUnion([{"mid": mid, "by": uid, "date": datetime.now()}])})

    elif message.content_type == 'media_group':
        for media in message.photo:
            mid = bot.forward_message(TARGET_CHANNEL_ID, message.chat.id, message.message_id).message_id

            db.document(isListening["files"]).update({"files": [{"mid": mid, "by": uid, "date": datetime.now()}]})

    bot.reply_to(message, "File saved successfully!")

bot.polling()