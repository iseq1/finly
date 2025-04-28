from app.bot.handlers.base import BaseHandler
from app.utils.auth import TelegramAuthService
from app.exceptions.telegram_exceptions import TelegramAuthError
from app.utils.logger import logger

class TelegramRegisterHandler(BaseHandler):

    async def handle(self, event, state, context=None):
        logger.debug(f"[{self.__class__.__name__}] Регистрация нового пользователя {event.from_user.id}")
        try:
            auth = TelegramAuthService()
            data, _ = await auth.register(
                tg_id=event.from_user.id,
                tg_username=event.from_user.username
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
            logger.info(f"[{self.__class__.__name__}] Успешная регистрация: user_id={data_from_context['user_id']}")
            return await super().handle(event, state, data_from_context)

        except TelegramAuthError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка регистрации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при регистрации пользователя: {e}")
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


class SendWelcomeHandler(BaseHandler):
    async def handle(self, event, state, context=None):
        from app.bot.keyboards.main_manu import MainMenuKeyboard
        logger.debug(f"[{self.__class__.__name__}] Приветственное сообщение отправлено пользователю {event.from_user.id}")
        await event.message.edit_text("👋 Вы успешно прошли регистрацию и теперь вам доступен основной функционал системы! Вы можете продолжить перейдя в главное меню по кнопке ниже:", reply_markup=MainMenuKeyboard.go_to_main_menu_keyboard())