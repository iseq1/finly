from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.bot.handlers.menu.profile.chain import ProfileMenuChain
from app.bot.states import EditProfileState

router = Router()

@router.callback_query(F.data == "me_menu")
async def handle_profile_menu(callback: CallbackQuery, state: FSMContext):
    chain = ProfileMenuChain().get_profile_chain()
    await chain.handle(callback, state)

@router.callback_query(F.data == "put_me_menu")
async def handle_link_telegram(callback: CallbackQuery, state: FSMContext):
    chain = ProfileMenuChain().get_profile_chain()
    await chain.handle(callback, state)

@router.callback_query(F.data == "change_profile_info_menu", EditProfileState.waiting_for_choosing_action)
async def change_profile_info(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    step = data.get("chain_step", 6)

    handler = ProfileMenuChain().get_handler_by_step(step)
    if handler:
        result = await handler.handle(callback, state)
        if result is not False:
            await state.update_data(chain_step=step + 1)

    await callback.answer()


@router.callback_query(F.data.startswith('change_'), EditProfileState.choosing_field)
async def process_field_choice(callback: CallbackQuery, state: FSMContext):
    field_to_edit = callback.data.replace('change_', '')
    await state.update_data(field_to_edit=field_to_edit)

    data = await state.get_data()
    step = data.get("chain_step", 7)

    handler = ProfileMenuChain().get_handler_by_step(step)
    if handler:
        result = await handler.handle(callback, state)
        if result is not False:
            await state.update_data(chain_step=step + 1)
    await callback.answer()


@router.message(EditProfileState.waiting_for_value)
async def handle_field_input(message: Message, state: FSMContext):
    data = await state.get_data()
    step = data.get("chain_step", 8)

    handler = ProfileMenuChain().get_handler_by_step(step)
    if handler:
        result = await handler.handle(message, state)
        if result is not False:
            await state.update_data(chain_step=step + 1)










