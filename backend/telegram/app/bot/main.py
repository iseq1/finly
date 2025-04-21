import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.bot.handlers import start
import os

TOKEN = os.getenv("TG_BOT_TOKEN")

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)

    await dp.start_polling(bot)
