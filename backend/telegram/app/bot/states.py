from aiogram.fsm.state import State, StatesGroup

class AuthState(StatesGroup):
    authenticated = State()
    waiting_for_email = State()
    waiting_for_password = State()

class EditProfileState(StatesGroup):
    waiting_for_choosing_action = State()
    choosing_field = State()
    waiting_for_value = State()