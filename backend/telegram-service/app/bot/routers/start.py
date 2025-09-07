# routers/main.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.bot.handlers.start.chain import StartChain

router = Router()

@router.message(F.text == "/start")
async def start_script(message: Message, state: FSMContext):
    chain = StartChain().get_start_chain()
    await chain.handle(message, state)
