import aiogram
from app.bot.keyboards.start import StartKeyboard

class TelegramAuthError(Exception):
    """Базовая ошибка Telegram авторизации."""
    def __init__(self, message: str = "Ошибка авторизации", code: int = None):
        self.message = message
        self.code = code
        super().__init__(message)

    def to_user_message(self) -> str:
        """Сообщение, отображаемое пользователю."""
        return "❗ Произошла ошибка при авторизации. Попробуйте снова."

    def to_user_message_with_markup(self) -> tuple[str, aiogram.types.InlineKeyboardMarkup | None]:
        return self.to_user_message(), None  # По умолчанию клавиатура отсутствует


class TelegramLoginNotFound(TelegramAuthError):
    def __init__(self):
        super().__init__("Пользователь с таким Telegram ID не найден.", code=404)

    def to_user_message(self) -> str:
        return "👤 Пользователь не найден. Хотите зарегистрироваться?"

    def to_user_message_with_markup(self):
        text = self.to_user_message()
        keyboard = StartKeyboard().get_register_keyboard()
        return text, keyboard


class TelegramRegisterExisted(TelegramAuthError):
    def __init__(self):
        super().__init__("Пользователь с таким Telegram ID уже существует.", code=404)

    def to_user_message(self) -> str:
        return "👤 Пользователь уже есть в системе. Хотите авторизоваться?"

    def to_user_message_with_markup(self):
        text = self.to_user_message()
        keyboard = StartKeyboard().get_login_keyboard()
        return text, keyboard


class TelegramIdentityExisted(TelegramAuthError):
    def __init__(self):
        super().__init__("Пользователь с такой Telegram айдентикой уже существует.", code=406)

    def to_user_message(self) -> str:
        return "👤 Пользователь уже есть в системе. Хотите авторизоваться?"

    def to_user_message_with_markup(self):
        text = self.to_user_message()
        keyboard = StartKeyboard().get_login_keyboard()
        return text, keyboard


class TelegramUnauthorizedError(TelegramAuthError):
    def __init__(self):
        super().__init__("Пользователь с таким Telegram ID деактивирован.", code=401)

    def to_user_message(self) -> str:
        return "🔒 Ваш аккаунт деактивирован. Обратитесь в поддержку."


class TelegramIncorrectLoginError(TelegramAuthError):
    def __init__(self):
        super().__init__("Пользователь с таким email и/или паролем не найден.", code=404)

    def to_user_message(self) -> str:
        return "⚠️ Неверный логин или пароль. Попробуйте ещё раз.\nИли зарегистрируйтесь, если ещё не успели сделать это:"

    def to_user_message_with_markup(self):
        text = self.to_user_message()
        keyboard = StartKeyboard().get_register_keyboard()
        return text, keyboard


class TelegramForbiddenError(TelegramAuthError):
    def __init__(self):
        super().__init__("Неверный ключ или доступ запрещён.", code=403)

    def to_user_message(self) -> str:
        return "⛔ Доступ запрещён. Проверьте данные или обратитесь в поддержку."


class TelegramConnectionError(TelegramAuthError):
    def __init__(self):
        super().__init__("Проблема с подключением к серверу.", code=503)

    def to_user_message(self) -> str:
        return "🌐 Сервер временно недоступен. Попробуйте позже."


class TelegramValidationError(TelegramAuthError):
    def __init__(self):
        super().__init__("Ошибка валидации данных.", code=400)

    def to_user_message(self) -> str:
        return "⚠️ Сервер возвращает ошибку. Обратитесь в поддержку."

class TelegramUnexpectedResponse(TelegramAuthError):
    def __init__(self, status_code: int):
        super().__init__(f"Неожиданный код ответа от сервера: {status_code}", code=status_code)

    def to_user_message(self) -> str:
        return "❗ Неизвестная ошибка сервера. Попробуйте снова или напишите в поддержку."