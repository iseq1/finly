import httpx
from app.config import API_BASE_URL
from app.utils.logger import logger
from app.exceptions.request_exceptions import (
    RequestServerUnavailableError, RequestBadRequestError, RequestForbiddenError, RequestNotFoundError,
    RequestConflictError, RequestTooManyRequestsError, RequestUnauthorizedError, RequestUnexpectedError,
    TokenStorageError
)

class RequestManager:
    def __init__(self):
        self.base_url = API_BASE_URL

    async def fetch_and_attach_entity_info(self, budgets, field_name, api_path_template, state):
        ids_to_fetch = list({budget[field_name] for budget in budgets if budget.get(field_name, 0) != 0})
        if not ids_to_fetch:
            return

        entity_list = await self.make_request(
            method='POST',
            url=api_path_template,
            state=state,
            json={'ids': ids_to_fetch},
        )

        return entity_list


    async def make_request(self, method, url, state, **kwargs):
        logger.debug(f"[{self.__class__.__name__}] [MakeRequest] Попытка создания запроса {method} к серверу от пользователя: {(await state.get_data()).get('user_id')}")
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
        except httpx.RequestError as e:
            logger.error(f"[{self.__class__.__name__}] 🔴 Ошибка подключения к API при запросе: {e}")
            raise RequestServerUnavailableError()



        if status in (200, 201):
            logger.debug(f"[{self.__class__.__name__}] 🟢 [MakeRequest] Запрос {method} успешен.")
            if new_access_token != access_token or new_refresh_token != refresh_token:
                await self.set_user_tokens(state, new_access_token, new_refresh_token)
            return data

        errors_by_code = {
            400: RequestBadRequestError,
            403: RequestForbiddenError,
            404: RequestNotFoundError,
            409: RequestConflictError,
            429: RequestTooManyRequestsError,
            401: RequestUnauthorizedError,
        }
        exception_cls = errors_by_code.get(status, RequestUnexpectedError)
        raise exception_cls() if status in errors_by_code else exception_cls(status)

    @staticmethod
    async def make_authenticated_request(session, method, url, access_token, refresh_token, refresh_url, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {access_token}'
        headers['Content-Type'] = f'application/json'

        response = await session.request(method, url, headers=headers, **kwargs)
        print(kwargs)
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
            print(type(data), data)
            if isinstance(data, dict):
                if data.get('errors', False):
                    print(data['errors'])
            return response.status_code, data, access_token, refresh_token

    @staticmethod
    async def set_user_tokens(state, access_token, refresh_token):
        """Сохраняет токены в состояние пользователя."""
        user_id = (await state.get_data()).get("user_id")
        logger.debug(f"[SetUserTokens] Сохранение токенов пользователя: {user_id}")
        data_from_context = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        await state.update_data(data_from_context)

    @staticmethod
    async def get_user_tokens(state):
        """Получает токены из состояния пользователя. Бросает исключение, если токены не найдены."""
        user_id = (await state.get_data()).get("user_id")
        logger.debug(f"[GetUserTokens] Получение токенов пользователя: {user_id}")

        data = await state.get_data()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")

        if not access_token or not refresh_token:
            logger.debug(f"[GetUserTokens] Токены не найдены или неполные у пользователя: {user_id}")
            raise TokenStorageError()

        return access_token, refresh_token