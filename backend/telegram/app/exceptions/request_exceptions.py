import aiogram
from app.bot.keyboards.start import StartKeyboard

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


class RequestStatusCodeError(RequestError):
    def __init__(self, message: str = "Ошибка запроса", code: int = None):
        super().__init__(message=message, code=code)

    def to_user_message(self) -> str:
        return f"❗ Ошибка при выполнении запроса ({self.code}). Попробуйте позже."


class RequestBadRequestError(RequestStatusCodeError):
    def __init__(self):
        super().__init__("Некорректный запрос", code=400)

    def to_user_message(self) -> str:
        return "⚠️ Некорректный запрос. Пожалуйста, проверьте введённые данные."


class RequestForbiddenError(RequestStatusCodeError):
    def __init__(self):
        super().__init__("Доступ запрещён", code=403)

    def to_user_message(self) -> str:
        return "🚫 У вас нет прав для выполнения этого действия."


class RequestNotFoundError(RequestStatusCodeError):
    def __init__(self):
        super().__init__("Ресурс не найден", code=404)

    def to_user_message(self) -> str:
        return "🔍 Запрашиваемый ресурс не найден."


class RequestConflictError(RequestStatusCodeError):
    def __init__(self):
        super().__init__("Конфликт данных", code=409)

    def to_user_message(self) -> str:
        return "⚠️ Конфликт данных. Пожалуйста, попробуйте снова."


class RequestTooManyRequestsError(RequestStatusCodeError):
    def __init__(self):
        super().__init__("Слишком много запросов", code=429)

    def to_user_message(self) -> str:
        return "⏳ Вы делаете слишком много запросов. Пожалуйста, подождите."


class TokenStorageError(RequestError):
    def __init__(self):
        super().__init__("Отсутствуют токены доступа и обновления.", code=404)

    def to_user_message(self) -> str:
        return "🔒 Ваша сессия истекла. Пожалуйста, авторизуйтесь заново."

    def to_user_message_with_markup(self):
        text = self.to_user_message()
        keyboard = StartKeyboard().get_login_keyboard()
        return text, keyboard