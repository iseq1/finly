class TelegramLinkError(Exception):
    """Базовая ошибка связи Telegram и системы."""
    def __init__(self, message: str = "Ошибка связи Telegram и системы", code: int = None):
        self.message = message
        self.code = code
        super().__init__(message)

    def to_user_message(self) -> str:
        """Сообщение, отображаемое пользователю."""
        return "❗ Произошла ошибка при связи Telegram и системы. Попробуйте снова."


class IncorrectUserInputError(TelegramLinkError):
    def __init__(self):
        super().__init__("Пользователь ввёл некорректный символы.", code=418)

    def to_user_message(self) -> str:
        return "⚠️ Вы ввели некорректный электронный адрес. Попробуйте снова."


class IncorrectEmailError(TelegramLinkError):
    def __init__(self):
        super().__init__("Пользователь ввёл некорректный электронный андрес.", code=418)

    def to_user_message(self) -> str:
        return "⚠️ Вы ввели некорректный электронный адрес. Попробуйте снова."