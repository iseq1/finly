from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.bot.handlers.menu.budget.chain import BudgetMenuChain
from app.bot.states import BudgetState

router = Router()

@router.callback_query(F.data == 'get_my_budget_menu')
async def my_budgets_menu(callback: CallbackQuery, state: FSMContext):
    chain = BudgetMenuChain().get_user_budgets_chain()
    await chain.handle(callback, state)

@router.callback_query(F.data == "user_budget_next", BudgetState.choosing_budget_item)
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    budgets = data.get("budgets", [])

    index = (data.get("budget_index", 0) + 1) % len(budgets)
    await state.update_data(budget_index=index)

    handler = BudgetMenuChain().get_handler_by_step(6, BudgetMenuChain().get_user_budgets_chain)
    if handler:
        await handler.handle(callback, state)

    await callback.answer()

@router.callback_query(F.data == "user_budget_prev", BudgetState.choosing_budget_item)
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    budgets = data.get("budgets", [])
    index = (data.get("budget_index", 0) - 1) % len(budgets)
    await state.update_data(budget_index=index)

    handler = BudgetMenuChain().get_handler_by_step(6, BudgetMenuChain().get_user_budgets_chain)
    if handler:
        await handler.handle(callback, state)

    await callback.answer()

@router.callback_query(F.data == "select_user_budget")
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    budgets = data.get("budgets", [])
    index = (data.get("budget_index", 0)) % len(budgets)
    await state.update_data(budget_index=index)

    handler = BudgetMenuChain().get_handler_by_step(7, BudgetMenuChain().get_user_budgets_chain)
    if handler:
        await handler.handle(callback, state)

    await callback.answer()

@router.callback_query(F.data == "get_my_balance_snapshot_menu")
async def next_cashbox(callback: CallbackQuery, state: FSMContext):
    chain = BudgetMenuChain().get_user_snapshot_balance_chain()
    await chain.handle(callback, state)