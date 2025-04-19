import logging
from aiogram import Bot, Dispatcher, types
from app.config import Config

logging.basicConfig(level=logging.INFO)

API_TOKEN = Config.TG_BOT_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# Пример хендлера
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я твой бот.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
