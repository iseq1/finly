
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.handlers.auth.register.chain import RegisterChain

router = Router()

@router.callback_query(F.data == "auth_register")
async def handle_register(callback: CallbackQuery, state: FSMContext):
    chain = RegisterChain().get_register_chain()
    await chain.handle(callback, state)
