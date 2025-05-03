import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.bot.routers import start, auth_login, auth_register, auth_link, main_menu, profile, transaction
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TG_BOT_TOKEN")


async def main():

    if TOKEN is None:
        raise ValueError("TG_BOT_TOKEN is not set in environment variables.")

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(auth_login.router)
    dp.include_router(auth_register.router)
    dp.include_router(auth_link.router)
    dp.include_router(main_menu.router)
    dp.include_router(profile.router)
    dp.include_router(transaction.router)

    await dp.start_polling(bot)
