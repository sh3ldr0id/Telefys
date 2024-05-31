from app import bot

def fetchName(uid):
    try:
        chat = bot.get_chat(uid)

        first_name = chat.first_name
        last_name = chat.last_name

        user_name = f"{first_name} {last_name}" if last_name else first_name

        return user_name
    
    except Exception as e:
        print(f"Error fetching user name: {e}")
        
        return None