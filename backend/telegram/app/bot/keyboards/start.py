from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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
