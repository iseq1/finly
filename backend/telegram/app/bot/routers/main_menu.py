from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from app.bot.handlers.menu.chain import MainMenuChain

router = Router()

@router.callback_query(F.data == "main_menu")
async def handle_link_telegram(callback: CallbackQuery, state: FSMContext):
    chain = MainMenuChain().get_start_chain()
    await chain.handle(callback, state)

@router.callback_query(F.data == "profile_menu")
async def handle_link_telegram(callback: CallbackQuery, state: FSMContext):
    chain = MainMenuChain().get_profile_chain()
    await chain.handle(callback, state)