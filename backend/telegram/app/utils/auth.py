import httpx
from app.config import API_BASE_URL, SECRET_TELEGRAM_AUTH_KEY
from app.utils.logger import logger
from app.exceptions.telegram_exceptions import (
    TelegramLoginNotFound,
    TelegramForbiddenError,
    TelegramUnauthorizedError,
    TelegramUnexpectedResponse,
)



class TelegramAuthService:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.secret = SECRET_TELEGRAM_AUTH_KEY

    async def login(self, tg_id: int, tg_username: str):
        payload = self._build_payload(tg_id, tg_username)
        url = f"{self.base_url}/auth/telegram/login"

        logger.debug(f"[{self.__class__.__name__}] 🟡 [Login] Попытка логина пользователя {tg_username} ({tg_id})")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
        except httpx.RequestError as e:
            logger.error(f"[TelegramAuthService] 🔴 Ошибка подключения к API при логине: {e}")
            raise TelegramUnexpectedResponse(503)

        if response.status_code == 200:
            logger.debug(f"[TelegramAuthService] 🟢 Успешный логин для {tg_username}")
            return response.json(), False

        errors_by_code = {
            401: TelegramUnauthorizedError,
            403: TelegramForbiddenError,
            404: TelegramLoginNotFound,
        }
        exception_cls = errors_by_code.get(response.status_code, TelegramUnexpectedResponse)
        raise exception_cls() if response.status_code in errors_by_code else exception_cls(response.status_code)


    async def register(self, tg_id: int, tg_username: str):
        payload = self._build_payload(tg_id, tg_username)
        url = f"{self.base_url}/auth/telegram/register"

        logger.debug(f"[TelegramAuthService] 🟡 [Register] Регистрация пользователя {tg_username} ({tg_id})")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
        except httpx.RequestError as e:
            logger.error(f"[TelegramAuthService] 🔴 Ошибка подключения к API при регистрации: {e}")
            raise TelegramConnectionError("Сервер авторизации недоступен.")

        if response.status_code == 201:
            logger.debug(f"[TelegramAuthService] 🟢 Успешная регистрация пользователя {tg_username}")
            return response.json(), True
        elif response.status_code == 400:
            raise TelegramRegisterConflict(response.json().get("message", "Конфликт регистрации"))
        elif response.status_code == 403:
            raise TelegramAuthError("Неверный ключ или доступ запрещён.")
        else:
            raise TelegramAuthError(f"Неожиданный код ответа: {response.status_code}")

    async def auth_link_telegram(self, email: str, password: str):
        url = f"{self.base_url}/auth/login"
        payload = {
            "email": email,
            "password": password,
            "remember_me": True
        }

        logger.debug(f"[TelegramAuthService] 🟡 [AuthLink] Попытка входа через email: {email}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
        except httpx.RequestError as e:
            logger.error(f"[TelegramAuthService] 🔴 Ошибка подключения к API при авторизации через email: {e}")

            raise TelegramConnectionError("Сервер авторизации недоступен.")

        if response.status_code != 200:
            raise TelegramAuthError("❌ Неверный email или пароль.")

        logger.debug(f"[TelegramAuthService] 🟢 Email авторизация успешна: {email}")

        return response.json(), True

    async def link_telegram(self, tg_id: int, tg_username: str, access_token: str):
        url = f"{self.base_url}/auth/me/telegram"
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {
            "telegram_id": tg_id,
            "telegram_username": tg_username or ""
        }

        logger.debug(f"[TelegramAuthService] 🟡 [LinkTelegram] Привязка Telegram пользователя {tg_username} ({tg_id})")


        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
        except httpx.RequestError as e:
            logger.error(f"[TelegramAuthService] 🔴 Ошибка подключения при привязке Telegram: {e}")

            raise TelegramConnectionError("Сервер авторизации недоступен.")

        if response.status_code != 201:
            raise TelegramAuthError("⚠️ Не удалось привязать Telegram. Попробуйте позже.")

        logger.debug(f"[TelegramAuthService] 🟢 Telegram привязан к аккаунту {tg_username}")

        return response.json(), True

    def _build_payload(self, tg_id: int, tg_username: str):
        return {
            "telegram_id": tg_id,
            "telegram_username": tg_username,
            "secret": self.secret
        }
