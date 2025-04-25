from app.bot.handlers.base import BaseHandler
from app.bot.keyboards.start import StartKeyboard
from app.utils.logger import logger


class SendStartMessageHandler(BaseHandler):
    async def handle(self, event, state, context=None):
        logger.debug(f"[SendStartMessageHandler] Отправка стартового сообщения пользователю {event.from_user.id}")

        await event.answer(
            "👋 Привет! Выберите, что хотите сделать:",
            reply_markup=StartKeyboard.get_start_keyboard()
        )

        return await super().handle(event, state, context)
