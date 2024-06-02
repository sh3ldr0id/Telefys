from app import bot
from app.helpers.constants import OPEN_FOLDER, DELETE

from app.handlers.callbacks import open_folder, delete

@bot.callback_query_handler(func=lambda x: True)
def callback_handler(callback):
    if callback.message and callback.data.startswith(OPEN_FOLDER):
        open_folder.open_folder(callback)

    elif callback.message and callback.data.startswith(DELETE):
        delete.delete(callback)