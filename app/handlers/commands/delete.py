from app import bot

@bot.message_handler(commands=["delete"])
def delete(message):
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:        
        if message.reply_to_message.content_type == "document":
            print("Done")

        bot.delete_message(chat_id, message_id_to_delete)
    else:
        bot.send_message(message.chat.id, "You need to reply to a file or folder with /delete to delete it.")