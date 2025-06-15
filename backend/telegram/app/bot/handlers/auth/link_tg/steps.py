import aiogram
from aiogram.fsm.context import FSMContext
from app.bot.handlers.base import BaseHandler
from app.bot.states import AuthState
from app.utils.auth import TelegramAuthService
from app.exceptions.telegram_exceptions import TelegramAuthError
from app.exceptions.link_tg_exceptions import (
    TelegramLinkError,
    IncorrectEmailError,
    IncorrectUserInputError,
)
from app.utils.logger import logger

class FirstStepTelegramLinkHandler(BaseHandler):

    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Связывание Tg-аккаунта  {event.from_user.id} и пользователя web-системы")
        logger.debug(f"[{self.__class__.__name__}] Запрос e-mail адреса пользователя {event.from_user.id}")
        await state.set_state(AuthState.waiting_for_email)
        await state.update_data(chain_step=1)

        text = "📧 Введите ваш email (example@gmail.com):"
        if isinstance(event, aiogram.types.CallbackQuery):
            await event.message.edit_text(text)
        elif isinstance(event, aiogram.types.Message):
            await event.answer(text)

        return False


class TakingEmaiHandler(BaseHandler):

    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение e-mail адреса пользователя {event.from_user.id}")
        try:
            if not isinstance(event.text, str):
                raise IncorrectUserInputError()

            email = event.text.strip()

            if "@" not in email or "." not in email:
                raise IncorrectEmailError()

            await state.update_data(email=email)
            return await super().handle(event, state, context)

        except TelegramLinkError as e:
            logger.warning(f"[{self.__class__.__name__}] Пользовательская ошибка: {e.message} | {event.from_user.id}")
            await event.answer(e.to_user_message())
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при обработке email: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
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
            if not isinstance(event.text, str):
                raise IncorrectUserInputError()
            password = event.text.strip()
            await state.update_data(password=password)
            return await super().handle(event, state, context)

        except TelegramLinkError as e:
            logger.warning(f"[{self.__class__.__name__}] Пользовательская ошибка: {e.message} | {event.from_user.id}")
            await event.answer(e.to_user_message())
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при обработке пароля: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
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

        except TelegramLinkError as e:
            logger.warning(f"[{self.__class__.__name__}] Ошибка при взаимодействии с Telegram UI: {event.from_user.id}")
            await event.answer(e.to_user_message())
            return False
        except TelegramAuthError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка авторизации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)

            # Перезапуск цепочки
            from app.bot.handlers.auth.link_tg.chain import LinkTelegramChain
            await state.clear()
            first_handler = LinkTelegramChain().get_handler_by_step(0)
            return await first_handler.handle(event, state)
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False



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

        try:
            data = await state.get_data()
            access_token = data.get("access_token")
            auth = TelegramAuthService()
            user_data, _ = await auth.link_telegram(tg_id=event.from_user.id,
                                               tg_username=event.from_user.username or "",
                                               access_token=access_token)
            return await super().handle(event, state, context)

        except TelegramAuthError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка соединения пользователя телеграмм и пользователя системы: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная соединения пользователя телеграмм и пользователя системы: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False



class SendWelcomeHandler(BaseHandler):
    async def handle(self, event, state, context=None):
        from app.bot.keyboards.main_manu import MainMenuKeyboard
        logger.debug(f"[{self.__class__.__name__}] Приветственное сообщение отправлено пользователю {event.from_user.id}")
        await event.message.edit_text("👋 Добро пожаловать!\n\n"
                                      "Теперь вам открыт доступ ко всем основным функциям системы.\n"
                                      "Вы можете приступить к работе — просто нажмите кнопку ниже, чтобы перейти в главное меню.\n",
                                      reply_markup=MainMenuKeyboard.go_to_main_menu_keyboard())