from aiogram.fsm.context import FSMContext
from app.bot.handlers.base import BaseHandler
from app.bot.keyboards.main_manu import MainMenuKeyboard
from app.bot.keyboards.profile import ProfileKeyboard
from app.utils.logger import logger


class SendMainMenuMessageHandler(BaseHandler):
    async def handle(self, event, state, context=None):
        logger.debug(f"[{self.__class__.__name__}] Отправка сообщения с главным меню авторизированному пользователю {event.from_user.id}")

        await event.message.edit_text(
            text="Главное меню:",
            reply_markup=MainMenuKeyboard().get_main_menu_keyboard()
        )

        return await super().handle(event, state, context)


class SendProfileHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Отправка сообщения с меню профиля авторизированному пользователю {event.from_user.id}")

        await event.message.edit_text(
            text='Меню профиля:',
            reply_markup=ProfileKeyboard.get_profile_menu_keyboard()
        )