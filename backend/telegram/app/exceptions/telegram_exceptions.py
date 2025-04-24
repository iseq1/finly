class TelegramAuthError(Exception):
    """Базовая ошибка Telegram авторизации."""
    def __init__(self, message: str = "Ошибка авторизации", code: int = None):
        self.message = message
        self.code = code
        super().__init__(message)

    def to_user_message(self) -> str:
        """Сообщение, отображаемое пользователю."""
        return "❗ Произошла ошибка при авторизации. Попробуйте снова."


class TelegramLoginNotFound(TelegramAuthError):
    def __init__(self):
        super().__init__("Пользователь с таким Telegram ID не найден.", code=404)

    def to_user_message(self) -> str:
        return "👤 Пользователь не найден. Хотите зарегистрироваться?"


class TelegramUnauthorizedError(TelegramAuthError):
    def __init__(self):
        super().__init__("Пользователь с таким Telegram ID деактивирован.", code=401)

    def to_user_message(self) -> str:
        return "🔒 Ваш Telegram-аккаунт деактивирован. Обратитесь в поддержку."


class TelegramForbiddenError(TelegramAuthError):
    def __init__(self):
        super().__init__("Неверный ключ или доступ запрещён.", code=403)

    def to_user_message(self) -> str:
        return "⛔ Доступ запрещён. Проверьте данные или обратитесь в поддержку."


class TelegramConnectionError(TelegramAuthError):
    def __init__(self):
        super().__init__("Проблема с подключением к серверу авторизации.", code=503)

    def to_user_message(self) -> str:
        return "🌐 Сервер временно недоступен. Попробуйте позже."


class TelegramUnexpectedResponse(TelegramAuthError):
    def __init__(self, status_code: int):
        super().__init__(f"Неожиданный код ответа от сервера: {status_code}", code=status_code)

    def to_user_message(self) -> str:
        return "❗ Неизвестная ошибка сервера. Попробуйте снова или напишите в поддержку."
