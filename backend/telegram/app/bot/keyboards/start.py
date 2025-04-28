from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class StartKeyboard:

    @staticmethod
    def get_link_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔗 Привязать Telegram", callback_data="auth_link_telegram"),
                ]
            ]
        )

    @staticmethod
    def get_register_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🆕 Зарегистрироваться", callback_data="auth_register"),
                ]
            ]
        )

    @staticmethod
    def get_login_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔐 Авторизоваться", callback_data="auth_login"),
                ]
            ]
        )

    @staticmethod
    def get_start_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔐 Авторизация", callback_data="auth_login"),
                    InlineKeyboardButton(text="🆕 Регистрация", callback_data="auth_register"),
                ],
                [
                    InlineKeyboardButton(text="🔗 Привязать Telegram", callback_data="auth_link_telegram")
                ]
            ]
        )