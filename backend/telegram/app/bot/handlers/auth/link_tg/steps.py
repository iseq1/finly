from aiogram.fsm.context import FSMContext
from app.bot.handlers.base import BaseHandler
from app.bot.states import AuthState
from app.utils.auth import TelegramAuthService
from app.exceptions.telegram_exceptions import TelegramAuthError
from app.utils.logger import logger

class FirstStepTelegramLinkHandler(BaseHandler):

    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Связывание Tg-аккаунта  {event.from_user.id} и пользователя web-системы")
        logger.debug(f"[{self.__class__.__name__}] Запрос e-mail адреса пользователя {event.from_user.id}")
        await state.set_state(AuthState.waiting_for_email)
        await state.update_data(chain_step=1)
        await event.message.edit_text("📧 Введите ваш email (example@gmail.com):")
        return False


class TakingEmaiHandler(BaseHandler):

    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение e-mail адреса пользователя {event.from_user.id}")
        try:
            email = event.text.strip()
            if "@" not in email or "." not in email:
                raise IncorrectEmailError('Некорректный email')

            await state.update_data(email=email)

            return await super().handle(event, state, context)

        except IncorrectEmailError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка получения e-mail пользователя: {event.from_user.id} ")
            await event.answer("⚠️ Некорректный email. Попробуйте снова")
            return False


class SecondStepTelegramLinkHandler(BaseHandler):

    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Запрос пароля пользователя {event.from_user.id}")
        await state.set_state(AuthState.waiting_for_password)
        await state.update_data(chain_step=3)
        await event.answer("🔐 Теперь введите пароль (password1!):")
        return False


class TakingPasswordHandler(BaseHandler):

    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение пароля пользователя {event.from_user.id}")
        try:
            password = event.text.strip()
            await state.update_data(password=password)
            return await super().handle(event, state, context)

        except IncorrectEmailError:
            logger.error(f"[{self.__class__.__name__}] Ошибка получения пароля пользователя: {event.from_user.id} ")
            return False


class TelegramLoginHandler(BaseHandler):

    async def handle(self, event, state, context=None):
        logger.debug(f"[{self.__class__.__name__}] Авторизация пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            email = data.get("email")
            password = data.get("password")

            auth = TelegramAuthService()
            data, _ = await auth.auth_link_telegram(
                email=email,
                password=password
            )
        except TelegramLoginNotFound:
            logger.warning(f"[{self.__class__.__name__}] Пользователь не найден: {event.from_user.id}")
            await event.answer("❌ Вы не зарегистрированы. Пожалуйста, сначала пройдите регистрацию.")
            return
        except TelegramAuthError:
            logger.error(f"[{self.__class__.__name__}] Ошибка авторизации пользователя: {event.from_user.id}")
            await event.answer("❌ Произошла ошибка авторизации. Обратитесь в поддержку.")
            return

        data_from_context = await state.get_data()

        if not data_from_context:
            data_from_context = {}

        data_from_context.update({
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "user_id": data["user"]["id"]
        })

        # Обновляем данные в FSMContext
        await state.update_data(data_from_context)
        logger.info(f"[{self.__class__.__name__}] Успешная авторизация: user_id={data_from_context['user_id']}")
        return await super().handle(event, state, data_from_context)


class FSMUpdateHandler(BaseHandler):
    async def handle(self, event, state, context=None):
        logger.debug(f"[{self.__class__.__name__}] Обновление FSM данных для user_id={context['user_id']}")
        await state.set_state("AuthState:authenticated")
        await state.update_data(
            access_token=context["access_token"],
            refresh_token=context["refresh_token"],
            user_id=context["user_id"]
        )
        return await super().handle(event, state, context)


class MakeLinkHandler(BaseHandler):

    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Установка соединения пользователя телеграмм и пользователя системы {event.from_user.id}")

        data = await state.get_data()
        access_token = data.get("access_token")

        try:
            auth = TelegramAuthService()
            user_data, _ = await auth.link_telegram(tg_id=event.from_user.id,
                                               tg_username=event.from_user.username or "",
                                               access_token=access_token)
        except TelegramAuthError:
            await event.answer("❌ Произошла ошибка связи между пользователем системы и телеграмм-аккаунтом.")
            logger.debug(f"[{self.__class__.__name__}] Ошибка соединения пользователя телеграмм и пользователя системы {event.from_user.id}")
            return False

        return await super().handle(event, state, context)


class SendWelcomeHandler(BaseHandler):
    async def handle(self, event, state, context=None):
        logger.debug(f"[{self.__class__.__name__}] Приветственное сообщение отправлено пользователю {event.from_user.id}")
        await event.answer("✅ Успешная авторизация и привязка Telegram!")
