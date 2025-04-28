import aiogram
from app.bot.keyboards.start import StartKeyboard

class TokenStorageError(Exception):
    """Ошибка при работе с токенами пользователя."""
    def __init__(self, message: str = "Ошибка сохранения или получения токенов пользователя"):
        self.message = message
        super().__init__(message)


class RequestError(Exception):
    """Базовая ошибка запросов к серверу."""
    def __init__(self, message: str = "Ошибка запроса к серверу", code: int = None):
        self.message = message
        self.code = code
        super().__init__(message)

    def to_user_message(self) -> str:
        """Сообщение, отображаемое пользователю."""
        return "❗ Ошибка соединения с сервером. Пожалуйста, попробуйте позже."

    def to_user_message_with_markup(self) -> tuple[str, aiogram.types.InlineKeyboardMarkup | None]:
        return self.to_user_message(), None


class RequestUnauthorizedError(RequestError):
    def __init__(self):
        super().__init__("Пользователь не авторизован.", code=401)

    def to_user_message(self) -> str:
        return "🔒 Ваша сессия истекла. Пожалуйста, авторизуйтесь заново."

    def to_user_message_with_markup(self):
        text = self.to_user_message()
        keyboard = StartKeyboard().get_login_keyboard()
        return text, keyboard


class RequestServerUnavailableError(RequestError):
    def __init__(self):
        super().__init__("Сервер недоступен.", code=503)

    def to_user_message(self) -> str:
        return "🌐 Сервер временно недоступен. Попробуйте позже."


class RequestUnexpectedError(RequestError):
    def __init__(self):
        super().__init__("Неожиданный ответ от сервера.", code=520)

    def to_user_message(self) -> str:
        return "❗ Произошла ошибка при обработке запроса. Попробуйте позже."
