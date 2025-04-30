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

@router.callback_query(F.data == "cashbox_menu")
async def handle_profile_menu(callback: CallbackQuery, state: FSMContext):
    chain = ProfileMenuChain().get_user_cashbox_chain()
    await chain.handle(callback, state)

@router.callback_query(F.data == "user_cashbox_details")
async def details_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_cashboxes = data.get("user_cashboxes", [])

    index = (data.get("user_cashbox_index", 0)) % len(user_cashboxes)
    await state.update_data(user_cashbox_index=index)
    await state.update_data(user_cashbox_details=True)

    from app.bot.handlers.menu.profile.steps import ShowUserCashbox
    handler = ShowUserCashbox()
    await handler.handle(callback, state)

@router.callback_query(F.data == "user_cashbox_back")
async def details_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_cashboxes = data.get("user_cashboxes", [])

    index = (data.get("user_cashbox_index", 0)) % len(user_cashboxes)
    await state.update_data(user_cashbox_index=index)
    await state.update_data(user_cashbox_details=False)

    from app.bot.handlers.menu.profile.steps import ShowUserCashbox
    handler = ShowUserCashbox()
    await handler.handle(callback, state)

@router.callback_query(F.data == "user_cashbox_next")
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_cashboxes = data.get("user_cashboxes", [])

    index = (data.get("user_cashbox_index", 0) + 1) % len(user_cashboxes)
    await state.update_data(user_cashbox_index=index)

    from app.bot.handlers.menu.profile.steps import ShowUserCashbox
    handler = ShowUserCashbox()
    await handler.handle(callback, state)

@router.callback_query(F.data == "user_cashbox_prev")
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_cashboxes = data.get("user_cashboxes", [])

    index = (data.get("user_cashbox_index", 0) - 1) % len(user_cashboxes)

    await state.update_data(user_cashbox_index=index)

    from app.bot.handlers.menu.profile.steps import ShowUserCashbox
    handler = ShowUserCashbox()
    await handler.handle(callback, state)

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


@router.callback_query(F.data == "create_user_cashbox")
async def create_user_cashbox(callback: CallbackQuery, state: FSMContext):
    chain = ProfileMenuChain().get_cashbox_menu_chain()
    await chain.handle(callback, state)


@router.callback_query(F.data == "back_to_profile_menu_from_providers_menu")
async def create_user_cashbox(callback: CallbackQuery, state: FSMContext):
    from app.bot.handlers.menu.profile.steps import ClearAfterProvidersHandler
    handler = ClearAfterProvidersHandler()
    await handler.handle(callback, state)


@router.callback_query(F.data == "provider_cashbox_next")
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cashbox_providers = data.get("cashbox_providers", [])

    index = (data.get("cashbox_providers_index", 0) + 1) % len(cashbox_providers)
    await state.update_data(cashbox_providers_index=index)

    from app.bot.handlers.menu.profile.steps import ShowCashboxProvidersHandler
    handler = ShowCashboxProvidersHandler()
    await handler.handle(callback, state)

@router.callback_query(F.data == "provider_cashbox_prev")
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cashbox_providers = data.get("cashbox_providers", [])

    index = (data.get("cashbox_providers_index", 0) - 1) % len(cashbox_providers)

    await state.update_data(cashbox_providers_index=index)

    from app.bot.handlers.menu.profile.steps import ShowCashboxProvidersHandler
    handler = ShowCashboxProvidersHandler()
    await handler.handle(callback, state)

@router.callback_query(F.data == "get_provider")
async def get_providers_cashboxes(callback: CallbackQuery, state: FSMContext):
    chain = ProfileMenuChain().get_create_user_cashbox_chain()
    await chain.handle(callback, state)


@router.callback_query(F.data == "cashbox_by_provider_next")
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cashboxes_by_provider = data.get("cashboxes_by_provider", [])

    index = (data.get("cashbox_by_provider_index", 0) + 1) % len(cashboxes_by_provider)
    await state.update_data(cashbox_by_provider_index=index)

    from app.bot.handlers.menu.profile.steps import ShowCashboxesByProviderHandler
    handler = ShowCashboxesByProviderHandler()
    await handler.handle(callback, state)

@router.callback_query(F.data == "cashbox_by_provider_prev")
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cashboxes_by_provider = data.get("cashboxes_by_provider", [])

    index = (data.get("cashbox_by_provider_index", 0) - 1) % len(cashboxes_by_provider)
    await state.update_data(cashbox_by_provider_index=index)

    from app.bot.handlers.menu.profile.steps import ShowCashboxesByProviderHandler
    handler = ShowCashboxesByProviderHandler()
    await handler.handle(callback, state)


@router.callback_query(F.data == "cashbox_by_provider_take")
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    pass