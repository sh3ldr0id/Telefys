import telebot
from telebot import types

from firebase_admin.credentials import Certificate
from firebase_admin import initialize_app, firestore

from datetime import datetime

# CONSTS
TOKEN = "6606433414:AAFvjx9FmND5f7EZHzaajkoO6SKkit9MhI0"

TARGET_CHANNEL_ID = -1002168833752
BACKUP_CHANNEL_ID =  -1002184815414

ALLOWED_FILES = ['document', 'photo', 'video', 'audio', 'voice', 'media_group']

class cbd:
    WHITELIST = "whitelist"
    WHITELIST_VIEW = "whitelist_view"
    WHITELIST_ADD = "whitelist_add"
    REVOKE = "revoke_"
    ADMIN = "admin_"

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
    user = users_coll.document(uid).get()

    if not user.exists or not user.to_dict()["verified"]:
        bot.send_message(int(uid), f"Dear User, \nPlease ask an admin to verify your id ({uid})")
        
        return False
    
    return True

def isAdmin(uid):
    user = users_coll.document(uid).get()

    return user.exists and user.to_dict()["isAdmin"]

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
        user_uid = user.id
        user = user.to_dict()

        markup = types.InlineKeyboardMarkup(row_width=2)

        revoke = types.InlineKeyboardButton(
            "Enable" if not user["verified"] else "Disable", 
            callback_data=cbd.REVOKE+user_uid
        )
        markup.add(revoke)

        admin = types.InlineKeyboardButton(
            "Promote" if not user["isAdmin"] else "Demote",
            callback_data=cbd.ADMIN+user_uid
        )
        markup.add(admin)

        bot.send_message(int(uid), f"{'🪪' if isAdmin(user_uid) else '👤'} {fetchName(user_uid)} ({user_uid})\n👥 {fetchName(user['by'])} ({user['by']})", reply_markup=markup)

def handle_whitelist_revoke(callback, user_uid):
    user_doc = users_coll.document(user_uid)

    user = user_doc.get()

    if user.exists:
        verified = not user.to_dict()['verified']
        user_doc.update({"verified": verified})

        bot.send_message(callback.message.chat.id, f"{fetchName(user.id)} ({user.id}) has access." if verified else f"{fetchName(user.id)} ({user.id}) no longer has access.")

def handle_whitelist_add(callback):
    global isListening

    uid = str(callback.message.chat.id)

    isListening["whitelist"].append(uid)

    bot.send_message(int(uid), "Please enter the user's uid.")

def handle_admin(callback, user_uid):
    user_doc = users_coll.document(user_uid)

    user = user_doc.get()

    if user.exists:
        isAdmin = not user.to_dict()['isAdmin']
        user_doc.update({"isAdmin": isAdmin})

        bot.send_message(callback.message.chat.id, f"{fetchName(user.id)} ({user.id}) now has admin access." if isAdmin else f"{fetchName(user.id)} ({user.id}) no longer has admin access.")

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

    if end_index == len(files) or len(files) < 10:
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

@bot.message_handler(commands=["cancel"])
def cancel(message):
    uid = str(message.chat.id)

    if uid in isListening["whitelist"]:
        isListening["whitelist"].remove(uid)

    if uid in isListening["name"]:
        isListening["name"].remove(uid)

    if uid in isListening["date"]:
        isListening["date"].pop(uid)
        
    if uid in isListening["files"]:
        isListening["files"].pop(uid)

    bot.reply_to(message, "Cancelled all activities.")

@bot.callback_query_handler(func=lambda call : True)
def answer(callback):
    uid = str(callback.message.chat.id)

    if not exists(uid):
        return

    if callback.message:
        cb = callback.data

        if isAdmin(uid):
            # Whitelist CRD
            if cb == cbd.WHITELIST:
                handle_whitelist(callback)

            elif cb == cbd.WHITELIST_ADD:
                handle_whitelist_add(callback)
                
            elif cb == cbd.WHITELIST_VIEW:
                handle_whitelist_view(callback)

            elif cb.startswith(cbd.REVOKE):
                handle_whitelist_revoke(callback, cb.split("_")[-1])

            elif cb.startswith(cbd.ADMIN):
                handle_admin(callback, cb.split("_")[-1])

        # Events CRD
        if cb == cbd.EVENTS:
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
def message(message):
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
        try:
            isListening["date"][uid]["date"] = datetime.strptime(message.text, '%d%m%Y')

        except ValueError:
            bot.reply_to(message, "Invalid format. Please Try again. (Eg: 09112001)")
            return

        events_coll.add(isListening["date"][uid])

        isListening["date"].pop(uid)

        bot.send_message(int(uid), "Done. I have created a new event for you.")

    elif uid in isListening["whitelist"]:
        isListening["whitelist"].remove(uid)

        user_doc = users_coll.document(message.text)

        user = user_doc.get()

        if user.exists and user.to_dict()["isAdmin"]:
            bot.send_message(message.chat.id, f"Resetting admin privileges for {fetchName(message.text)} ({message.text})")

        user_doc.set({
            "by": uid,
            "isAdmin": False
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
        bmid = bot.forward_message(BACKUP_CHANNEL_ID, message.chat.id, message.message_id).message_id

        events_coll.document(isListening["files"][uid]).update({"files": firestore.ArrayUnion([{"mid": mid, "bmid": bmid, "by": uid, "date": datetime.now()}])})

    elif message.content_type == 'media_group':
        for media in message.photo:
            mid = bot.forward_message(TARGET_CHANNEL_ID, message.chat.id, message.message_id).message_id
            bmid = bot.forward_message(BACKUP_CHANNEL_ID, message.chat.id, message.message_id).message_id

            events_coll.document(isListening["files"][uid]).update({"files": firestore.ArrayUnion([{"mid": mid, "bmid": bmid, "by": uid, "date": datetime.now()}])})

    bot.reply_to(message, "File saved successfully!")

bot.polling()