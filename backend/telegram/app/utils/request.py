import httpx
from app.config import API_BASE_URL
from app.utils.logger import logger
from app.exceptions.request_exceptions import (
    TokenStorageError,
    RequestError,
    RequestUnauthorizedError,
    RequestServerUnavailableError,
    RequestUnexpectedError,
)

class RequestManager:
    def __init__(self):
        self.base_url = API_BASE_URL

    async def make_request(self, method, url, state, **kwargs):
        try:
            logger.debug(f"[{self.__class__.__name__}] [MakeRequest] Попытка создания запроса {method} к серверу от пользователя: {(await state.get_data()).get('user_id')}")
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

            if status in (200, 201):
                logger.debug(f"[{self.__class__.__name__}] 🟢 [MakeRequest] Запрос {method} успешен.")

                if new_access_token != access_token or new_refresh_token != refresh_token:
                    await self.set_user_tokens(state, new_access_token, new_refresh_token)

                return data

            elif status == 401:
                logger.debug(f"[{self.__class__.__name__}] 🟡 [MakeRequest] Запрос {method} вернул 401.")
                raise RequestUnauthorizedError()
            else:
                logger.debug(f"[{self.__class__.__name__}] 🔴 [MakeRequest] Запрос {method} вернул неожиданный статус: {status}.")
                raise RequestUnexpectedError()

        except httpx.ConnectTimeout:
            raise RequestServerUnavailableError()
        except httpx.RequestError:
            raise RequestServerUnavailableError()
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] 🔥 Необработанная ошибка запроса: {e}")
            raise RequestError()

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
        logger.debug(f"[SetUserTokens] Сохранение токенов пользователя: {(await state.get_data()).get('user_id')}")
        try:
            data_from_context = {}
            data_from_context.update({
                "access_token": access_token,
                "refresh_token": refresh_token
            })
            await state.update_data(data_from_context)
        except Exception as e:
            logger.debug(f"[SetUserTokens] Ошибка при сохранении токенов пользователя: {(await state.get_data()).get('user_id')}")
            raise TokenStorageError(f"Не удалось сохранить токены: {e}")


    @staticmethod
    async def get_user_tokens(state):
        logger.debug(f"[SetUserTokens] Получение токенов пользователя: {(await state.get_data()).get('user_id')}")
        try:
            data = await state.get_data()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            if not access_token or not refresh_token:
                raise TokenStorageError("Токены пользователя отсутствуют в state.")
            return access_token, refresh_token
        except Exception as e:
            logger.debug(f"[SetUserTokens] Ошибка при получение токенов пользователя: {(await state.get_data()).get('user_id')}")
            raise TokenStorageError(f"Не удалось получить токены: {e}")