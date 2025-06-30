from aiogram import Bot

bot_instance: Bot = None

def set_bot(bot: Bot):
    global bot_instance
    bot_instance = bot

def get_bot() -> Bot:
    return bot_instance