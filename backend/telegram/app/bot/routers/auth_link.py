# routers/main.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.bot.handlers.auth.link_tg.chain import LinkTelegramChain
from app.bot.states import AuthState

router = Router()

@router.callback_query(F.data == "auth_link_telegram")
async def handle_link_telegram(callback: CallbackQuery, state: FSMContext):
    chain = LinkTelegramChain().get_link_chain()
    await chain.handle(callback, state)


@router.message(AuthState.waiting_for_email)
async def handle_email_input(message: Message, state: FSMContext):
    data = await state.get_data()
    step = data.get("chain_step", 1)

    handler = LinkTelegramChain().get_handler_by_step(step)
    if handler:
        result = await handler.handle(message, state)
        if result is not False:
            await state.update_data(chain_step=step + 1)


@router.message(AuthState.waiting_for_password)
async def handle_password_input(message: Message, state: FSMContext):
    data = await state.get_data()
    step = data.get("chain_step", 3)

    handler = LinkTelegramChain().get_handler_by_step(step)
    if handler:
        result = await handler.handle(message, state)
        if result is not False:
            await state.update_data(chain_step=step + 1)