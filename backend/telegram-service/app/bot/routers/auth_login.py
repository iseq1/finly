# routers/main.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.handlers.auth.login.chain import LoginChain

router = Router()

@router.callback_query(F.data == "auth_login")
async def handle_login(callback: CallbackQuery, state: FSMContext):
    chain = LoginChain().get_login_chain()
    await chain.handle(callback, state)
