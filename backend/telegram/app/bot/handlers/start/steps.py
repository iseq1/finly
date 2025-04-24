from app.bot.handlers.base import BaseHandler
from app.bot.keyboards.start import get_start_keyboard
from app.utils.logger import logger


class SendStartMessageHandler(BaseHandler):
    async def handle(self, event, state, context=None):
        logger.debug(f"[SendStartMessageHandler] Отправка стартового сообщения пользователю {event.from_user.id}")

        keyboard = get_start_keyboard()
        await event.answer(
            "👋 Привет! Выберите, что хотите сделать:",
            reply_markup=keyboard
        )

        return await super().handle(event, state, context)
