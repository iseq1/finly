from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.bot.handlers.menu.transaction.chain import TransactionMenuChain
from app.bot.states import EditProfileState, CreateNewUserCashbox, TransactionState

router = Router()

@router.callback_query(F.data == 'new_transaction_menu')
async def new_transaction_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    transaction_action = data.get('transaction_action', {})
    transaction_action['action'] = "create"
    await state.update_data(transaction_action=transaction_action)

    chain = TransactionMenuChain().get_transaction_chain()
    await chain.handle(callback, state)

@router.callback_query(F.data == 'transaction_history_menu')
async def new_transaction_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    transaction_action = data.get('transaction_action', {})
    transaction_action['action'] = "history"
    await state.update_data(transaction_action=transaction_action)

    chain = TransactionMenuChain().get_transaction_chain()
    await chain.handle(callback, state)

@router.callback_query(F.data == 'transaction_statistic_menu')
async def new_transaction_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    transaction_action = data.get('transaction_action', {})
    transaction_action['action'] = "statistic"
    await state.update_data(transaction_action=transaction_action)

    chain = TransactionMenuChain().get_transaction_chain()
    await chain.handle(callback, state)


@router.callback_query(F.data.startswith('transaction_type_'), TransactionState.waiting_for_transaction_field)
async def new_transaction_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    transaction_action = data.get('transaction_action', {})

    if callback.data == 'transaction_type_income':
        transaction_action['type'] = "income"
        await state.update_data(transaction_action=transaction_action)
    elif callback.data == 'transaction_type_expense':
        transaction_action['type'] = "expense"
        await state.update_data(transaction_action=transaction_action)
    else:
        pass


    if transaction_action['action'] == 'create':
        chain = TransactionMenuChain().get_create_transaction_chain()
        await chain.handle(callback, state)
    elif transaction_action['action'] == 'history':
        chain = TransactionMenuChain().get_watch_history_transaction_chain()
        await chain.handle(callback, state)
    elif transaction_action['action'] == 'statistic':
        pass
    else:
        pass


@router.callback_query(F.data == 'select_user_cashbox_for_transaction', TransactionState.waiting_for_transaction_user_cashbox)
async def select_category_for_transaction(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_cashboxes = data.get("user_cashboxes", [])
    index = (data.get("user_cashbox_index", 0)) % len(user_cashboxes)
    await state.update_data(user_cashbox_index=index)


    handler = TransactionMenuChain().get_handler_by_step(3, TransactionMenuChain.get_create_transaction_chain)
    if handler:
        await handler.handle(callback, state)

    await callback.answer()



@router.callback_query(F.data == "transaction_user_cashbox_next")
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_cashboxes = data.get("user_cashboxes", [])

    index = (data.get("user_cashbox_index", 0) + 1) % len(user_cashboxes)
    await state.update_data(user_cashbox_index=index)

    from app.bot.handlers.menu.transaction.steps import ShowUserCashboxHandler
    handler = ShowUserCashboxHandler()
    await handler.handle(callback, state)

@router.callback_query(F.data == "transaction_user_cashbox_prev")
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_cashboxes = data.get("user_cashboxes", [])
    index = (data.get("user_cashbox_index", 0) - 1) % len(user_cashboxes)
    await state.update_data(user_cashbox_index=index)

    from app.bot.handlers.menu.transaction.steps import ShowUserCashboxHandler
    handler = ShowUserCashboxHandler()
    await handler.handle(callback, state)


@router.callback_query(F.data == "select_category_next")
async def next_categories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("categories_index", 0)
    categories = data.get("categories", [])

    import math
    new_index = (index + 1) % math.ceil(len(categories) / 6)
    await state.update_data(categories_index=new_index)

    from app.bot.handlers.menu.transaction.steps import ShowCategoriesHandler
    handler = ShowCategoriesHandler()
    await handler.handle(callback, state)


@router.callback_query(F.data == "select_category_prev")
async def prev_categories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("categories_index", 0)
    categories = data.get("categories", [])

    import math
    new_index = (index - 1) % math.ceil(len(categories) / 6)
    await state.update_data(categories_index=new_index)

    from app.bot.handlers.menu.transaction.steps import ShowCategoriesHandler
    handler = ShowCategoriesHandler()
    await handler.handle(callback, state)


@router.callback_query(F.data.startswith('select_category_'), TransactionState.waiting_for_transaction_category)
async def select_category_for_transaction(callback: CallbackQuery, state: FSMContext):
    await state.update_data(categories_index=int(callback.data.split('_')[2]))

    handler = TransactionMenuChain().get_handler_by_step(7, TransactionMenuChain.get_create_transaction_chain)
    if handler:
        await handler.handle(callback, state)

    await callback.answer()


@router.callback_query(F.data == "select_subcategory_next")
async def next_categories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("subcategories_index", 0)
    subcategories = data.get("subcategories", [])

    import math
    new_index = (index + 1) % math.ceil(len(subcategories) / 6)
    await state.update_data(subcategories_index=new_index)

    from app.bot.handlers.menu.transaction.steps import ShowSubcategoriesHandler
    handler = ShowSubcategoriesHandler()
    await handler.handle(callback, state)


@router.callback_query(F.data == "select_subcategory_prev")
async def prev_categories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("subcategories_index", 0)
    subcategories = data.get("subcategories", [])

    import math
    new_index = (index - 1) % math.ceil(len(subcategories) / 6)
    await state.update_data(subcategories_index=new_index)

    from app.bot.handlers.menu.transaction.steps import ShowSubcategoriesHandler
    handler = ShowSubcategoriesHandler()
    await handler.handle(callback, state)


@router.callback_query(F.data.startswith('select_subcategory_'), TransactionState.waiting_for_transaction_subcategory)
async def select_category_for_transaction(callback: CallbackQuery, state: FSMContext):
    await state.update_data(subcategories_index=int(callback.data.split('_')[2]))

    handler = TransactionMenuChain().get_handler_by_step(11, TransactionMenuChain.get_create_transaction_chain)
    if handler:
        await handler.handle(callback, state)

    await callback.answer()


@router.callback_query(F.data.startswith('get_transaction_'), TransactionState.waiting_for_transaction_info)
async def select_category_for_transaction(callback: CallbackQuery, state: FSMContext):
    field = str(callback.data.split('_')[2])
    await state.update_data(get_transaction_field=field)

    handler = TransactionMenuChain().get_transaction_field_info_chain()
    if handler:
        await handler.handle(callback, state)

    await callback.answer()


@router.message(StateFilter(
    TransactionState.waiting_for_amount,
    TransactionState.waiting_for_comment,
    TransactionState.waiting_for_datetime,
    TransactionState.waiting_for_vendor,
    TransactionState.waiting_for_location,
    TransactionState.waiting_for_source
))
async def handle_field_input(message: Message, state: FSMContext):
    handler = TransactionMenuChain().get_handler_by_step(1, TransactionMenuChain().get_transaction_field_info_chain)
    if handler:
        await handler.handle(message, state)

@router.callback_query(F.data.startswith('get_create_new_'))
async def create_new_income(callback: CallbackQuery, state:FSMContext):
    handler = TransactionMenuChain().get_handler_by_step(14, TransactionMenuChain().get_create_transaction_chain)
    if handler:
        await handler.handle(callback, state)

    await callback.answer()











