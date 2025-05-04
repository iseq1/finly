from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.bot.handlers.menu.budget.chain import BudgetMenuChain

router = Router()

@router.callback_query(F.data == 'get_my_budget_menu')
async def my_budgets_menu(callback: CallbackQuery, state: FSMContext):
    # data = await state.get_data()
    # transaction_action = data.get('transaction_action', {})
    # transaction_action['action'] = "create"
    # await state.update_data(transaction_action=transaction_action)

    chain = BudgetMenuChain().get_user_budgets_chain()
    await chain.handle(callback, state)