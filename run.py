from app import bot

bot.polling(
    timeout=100,
    long_polling_timeout=100
)