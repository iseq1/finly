import aiogram
from app.bot.keyboards.profile import ProfileKeyboard

class ProfileError(Exception):
    """Базовая ошибка при работе с профилем."""
    def __init__(self, message: str = "Ошибка профиля", code: int = None):
        self.message = message
        self.code = code
        super().__init__(message)

    def to_user_message(self) -> str:
        return "❗ Произошла ошибка при получении данных профиля. Попробуйте позже."

    def to_user_message_with_markup(self) -> tuple[str, aiogram.types.InlineKeyboardMarkup | None]:
        return self.to_user_message(), None


class ProfileInfoUnavailable(ProfileError):
    def __init__(self):
        super().__init__("Профиль пользователя временно недоступен.", code=503)

    def to_user_message(self) -> str:
        return "⚠️ Не удалось загрузить ваш профиль. Попробуйте снова через некоторое время."

    def to_user_message_with_markup(self) -> tuple[str, aiogram.types.InlineKeyboardMarkup | None]:
        return self.to_user_message(), ProfileKeyboard.get_back_profile_menu_keyboard()