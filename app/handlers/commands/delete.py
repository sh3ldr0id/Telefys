from app import bot

@bot.message_handler(commands=["delete"])
def delete(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        message_id_to_delete = message.reply_to_message.message_id
        
        try:
            bot.delete_message(chat_id, message_id_to_delete)
            bot.send_message(chat_id, f"Message {message_id_to_delete} deleted.")
            
        except Exception as e:
            bot.send_message(chat_id, f"Failed to delete message {message_id_to_delete}. Error: {str(e)}")
    else:
        bot.send_message(message.chat.id, "You need to reply to a file or folder with /delete to delete it.")