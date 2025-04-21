from aiogram.fsm.state import State, StatesGroup

class AuthState(StatesGroup):
    authenticated = State()
    waiting_for_email = State()
    waiting_for_password = State()