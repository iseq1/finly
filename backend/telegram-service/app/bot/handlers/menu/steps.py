from aiogram.fsm.context import FSMContext
from app.bot.handlers.base import BaseHandler
from app.bot.keyboards.budget import BudgetKeyboard
from app.bot.keyboards.main_manu import MainMenuKeyboard
from app.bot.keyboards.profile import ProfileKeyboard
from app.bot.keyboards.transaction import TransactionKeyboard
from app.utils.logger import logger


class SendMainMenuMessageHandler(BaseHandler):
    async def handle(self, event, state, context=None):
        logger.debug(f"[{self.__class__.__name__}] Отправка сообщения с главным меню авторизированному пользователю {event.from_user.id}")

        await event.message.edit_text(
            text=(
                "📋 <b>Главное меню</b>\n\n"
                "👤 <b>Профиль</b> — управление аккаунтом и настройками\n"
                "💸 <b>Транзакции</b> — запись и просмотр операций\n"
                "📊 <b>Бюджеты</b> — настройка целей и контроль расходов\n\n"
                "Выберите раздел, чтобы продолжить 👇"
            ),
            reply_markup=MainMenuKeyboard().get_main_menu_keyboard(),
            parse_mode="HTML"
        )

        return await super().handle(event, state, context)


class SendProfileHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Отправка сообщения с меню профиля авторизированному пользователю {event.from_user.id}")

        await event.message.edit_text(
            text=(
                "👤 <b>Меню профиля</b>\n\n"
                "📄 <b>Личные данные</b> — имя, email и другие сведения\n"
                "🖼️ <b>Аватар пользователя</b> — управление фото профиля\n"
                "💼 <b>Мои кэш-боксы</b> — управление вашими кошельками\n\n"
                "⬅️ Вернуться в главное меню можно ниже"
            ),
            reply_markup=ProfileKeyboard.get_profile_menu_keyboard(),
            parse_mode="HTML"
        )
        return await super().handle(event, state, context)


class SendTransactionHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Отправка сообщения с меню транзакций авторизированному пользователю {event.from_user.id}")

        await event.message.edit_text(
            text=(
                "💳 <b>Меню транзакций</b>\n\n"
                "➕ <b>Записать новую транзакцию</b> — добавьте доход или расход\n"
                "📈 <b>Статистика</b> — анализ ваших трат и поступлений\n"
                "🕓 <b>История</b> — список всех ваших транзакций\n\n"
                "⬅️ Вернуться в главное меню можно ниже"
            ),
            reply_markup=TransactionKeyboard.get_transaction_menu_keyboard(),
            parse_mode="HTML"
        )


class SendBudgetHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Отправка сообщения с меню бюджета авторизированному пользователю {event.from_user.id}")

        await event.message.edit_text(
            text=(
                "📊 <b>Меню бюджета</b>\n\n"
                "📁 <b>Мои бюджеты</b> — просмотреть и управлять текущими бюджетами\n"
                "🆕 <b>Создать новый бюджет</b> — начните планировать новый финансовый поток\n"
                "💰 <b>Состояние баланса</b> — мгновенный снимок ваших доступных средств\n\n"
                "⬅️ Вернуться в главное меню можно ниже"
            ),
            reply_markup=BudgetKeyboard.get_budget_menu_keyboard(),
            parse_mode="HTML"
        )
        return await super().handle(event, state, context)
