"""
Базовый обработчик событий
"""
from aiogram.fsm.context import FSMContext
from app.utils.logger import logger

class BaseHandler:
    def __init__(self, next_handler: 'BaseHandler' = None):
        self.next_handler = next_handler

    async def handle(self, event, state: FSMContext, context: dict = None):
        class_name = self.__class__.__name__
        logger.debug(f"[{class_name}] Обработка событий: {event.__class__.__name__}")

        if self.next_handler:
            return await self.next_handler.handle(event, state, context or {})
