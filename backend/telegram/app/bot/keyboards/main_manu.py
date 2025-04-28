from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.keyboards.profile import ProfileKeyboard


class MainMenuKeyboard:

    @staticmethod
    def go_to_main_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    MainMenuKeyboard.get_main_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_main_menu_button():
        return InlineKeyboardButton(text='Главное меню', callback_data='main_menu')

    @staticmethod
    def back_to_main_menu_button():
        return InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')

    @staticmethod
    def get_main_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    ProfileKeyboard().get_profile_menu_button(),
                    InlineKeyboardButton(text='Транзакции', callback_data='transactions'),
                ],
                [
                    # ProfileKeyboard.get_profile_menu_button(),
                    InlineKeyboardButton(text='Транзакции', callback_data='transactions'),
                ],
                [
                    # ProfileKeyboard.get_profile_menu_button(),
                    InlineKeyboardButton(text='Транзакции', callback_data='transactions'),
                ]
            ]
        )