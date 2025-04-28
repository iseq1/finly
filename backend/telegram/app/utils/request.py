import httpx
from app.config import API_BASE_URL
from app.utils.logger import logger
from app.exceptions.telegram_exceptions import (
    TelegramLoginNotFound,
    TelegramForbiddenError,
    TelegramUnauthorizedError,
    TelegramUnexpectedResponse,
    TelegramConnectionError,
    TelegramValidationError,
    TelegramRegisterExisted,
    TelegramIncorrectLoginError,
    TelegramIdentityExisted
)

class RequestManager():
    def __init__(self):
        self.base_url = API_BASE_URL

    async def make_request(self, method, url, state, **kwargs):
        try:
            access_token, refresh_token = await self.get_user_tokens(state)
            async with httpx.AsyncClient() as session:
                 status, data, new_access_token, new_refresh_token = await self.make_authenticated_request(
                    session=session,
                    method=method,
                    url=f"{self.base_url}/{url}",
                    access_token=access_token,
                    refresh_token=refresh_token,
                    refresh_url=f"{self.base_url}/auth/refresh",
                    **kwargs
                )

            if status == 200 or status == 201:
                print("✅ Ответ от сервера:", data)

                # Если токены обновились - сохранить в объекте пользователя
                if new_access_token != access_token or new_refresh_token != refresh_token:
                    await self.set_user_tokens(state, new_access_token, new_refresh_token)
                return data
            else:
                # Нужно залогиниться заново
                print("Пользователь не авторизован, требуется логин")
        except Exception as e:
            pass

    @staticmethod
    async def make_authenticated_request(session, method, url, access_token, refresh_token, refresh_url, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {access_token}'

        response = await session.request(method, url, headers=headers, **kwargs)
        if response.status_code == 401:
            # Токен устарел, пробуем рефрешнуть
            refresh_headers = {'Authorization': f'Bearer {refresh_token}'}
            refresh_response = await session.post(refresh_url, headers=refresh_headers)
            if refresh_response.status_code == 200:
                data = refresh_response.json()
                new_access_token = data['access_token']
                new_refresh_token = data['refresh_token']

                # Переотправляем оригинальный запрос
                headers['Authorization'] = f'Bearer {new_access_token}'
                retry_response = await session.request(method, url, headers=headers, **kwargs)
                retry_data = retry_response.json()
                return retry_response.status_code, retry_data, new_access_token, new_refresh_token
            else:
                return 401, None, None, None
        else:
            data = response.json()
            return response.status_code, data, access_token, refresh_token


    @staticmethod
    async def set_user_tokens(state, access_token, refresh_token):
        """Заглушка: сюда можно добавить логику записи токенов"""
        print("💾 Сохраняем новые токены пользователя...")
        try:
            data_from_context = {}
            data_from_context.update({
                "access_token": access_token,
                "refresh_token": refresh_token
            })
            await state.update_data(data_from_context)
        except Exception as e:
            pass


    @staticmethod
    async def get_user_tokens(state):
        try:
            data = await state.get_data()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            return access_token, refresh_token
        except Exception as e:
            pass