from aiogram.fsm.state import State, StatesGroup

class AuthState(StatesGroup):
    authenticated = State()
    waiting_for_email = State()
    waiting_for_password = State()

class EditProfileState(StatesGroup):
    waiting_for_choosing_action = State()
    choosing_field = State()
    waiting_for_value = State()

class CreateNewUserCashbox(StatesGroup):
    waiting_for_balance = State()
    waiting_for_custom_name = State()
    waiting_for_note = State()

class TransactionState(StatesGroup):
    waiting_for_transaction_field = State()
    waiting_for_transaction_user_cashbox = State()
    waiting_for_transaction_category = State()
    waiting_for_transaction_subcategory = State()
    waiting_for_transaction_info = State()
    waiting_for_amount = State()
    waiting_for_comment = State()
    waiting_for_datetime = State()
    waiting_for_vendor = State()
    waiting_for_location = State()
    waiting_for_source = State()

class BudgetState(StatesGroup):
    choosing_budget_item = State()