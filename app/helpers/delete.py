from app import bot
from threading import Timer

def _delete(chat_id, messages):
    if type(messages) == list:
        try:
            bot.delete_message(chat_id, messages)

        except Exception as e:
            print(e)

    else:
        try:
            bot.delete_message(chat_id, messages)

        except Exception as e:
            print(e)
            

    

def deleteMessages(duration, chat_id, messages):
    Timer(duration, _delete, args=(chat_id, messages)).start()