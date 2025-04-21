import httpx
from app.config import API_BASE_URL, SECRET_TELEGRAM_AUTH_KEY

class TelegramAuthError(Exception):
    pass

class TelegramLoginNotFound(Exception):
    pass

class TelegramRegisterConflict(Exception):
    pass

async def telegram_auth(tg_id: int, tg_username: str, mode: str = "login", to_link=None):
    payload = {
        "telegram_id": tg_id,
        "telegram_username": tg_username,
        "secret": SECRET_TELEGRAM_AUTH_KEY
    }

    async with httpx.AsyncClient() as client:

        if mode == "login":
            response = await client.post(f"{API_BASE_URL}/auth/telegram/login", json=payload)
            if response.status_code == 200:
                return response.json(), False
            elif response.status_code == 404:
                raise TelegramLoginNotFound("Пользователь с таким Telegram ID не найден.")
            elif response.status_code == 403:
                raise TelegramAuthError("Неверный ключ или доступ запрещён.")
            elif response.status_code == 401:
                raise TelegramAuthError("Пользователь с таким Telegram ID деактивирован.")
            else:
                raise TelegramAuthError(f"Неожиданный код ответа: {response.status_code}")

        elif mode == "register":
            response = await client.post(f"{API_BASE_URL}/auth/telegram/register", json=payload)
            if response.status_code == 201:
                return response.json(), True
            elif response.status_code == 400:
                raise TelegramRegisterConflict(response.json()['message'])
            elif response.status_code == 403:
                raise TelegramAuthError("Неверный ключ или доступ запрещён.")
            else:
                raise TelegramAuthError(f"Неожиданный код ответа: {response.status_code}")

        elif mode == "auth_link_telegram":
            response = await client.post(f"{API_BASE_URL}/auth/login", json=to_link)
            if response.status_code != 200:
                raise TelegramAuthError("❌ Неверный email или пароль.")
            else:
                return response.json(), True

        else:
            raise ValueError("Недопустимый режим авторизации.")


async def link_telegram(tg_id, tg_username, access_token):

    async with httpx.AsyncClient() as client:
        link_response = await client.post(
            url=f"{API_BASE_URL}/auth/me/telegram",
            json={
                "telegram_id": tg_id,
                "telegram_username": tg_username
            },
            headers={"Authorization": f"Bearer {access_token}"})

        if link_response.status_code != 201:
            raise TelegramAuthError("⚠️ Не удалось привязать Telegram. Попробуйте позже.")
        else:
            return link_response.json(), True