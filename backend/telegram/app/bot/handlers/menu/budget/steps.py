import datetime

import aiogram.types
from aiogram.fsm.context import FSMContext
from app.bot.handlers.base import BaseHandler
from app.bot.keyboards.budget import BudgetKeyboard
from app.bot.states import BudgetState
from app.utils.request import RequestManager
from app.exceptions.request_exceptions import TokenStorageError, RequestError
from app.utils.logger import logger

class GetUserBudgetInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о бюджетах авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url=f'budget?month={datetime.datetime.utcnow().month}&year={datetime.datetime.utcnow().year}', state=state)
            if context is None:
                context = {}
            context['budgets'] = data
            return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except RequestError as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при обновлении информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при получении информации о бюджетах пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class CheckUserBudgetsInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Проверка бюджетов авторизированного пользователя {event.from_user.id}")
        try:
            budgets = context['budgets']
            if len(budgets) == 0:
                await event.message.edit_text(text='У вас пока нет ни единого зарегистрированного бюджета!', reply_markup=BudgetKeyboard().get_empty_budgets_menu_keyboard())
            else:
                await state.update_data(budgets=budgets)
                return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except RequestError as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при обновлении информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class GetCategoryInfoForBudgetsHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о категориях бюджетов авторизированного пользователя {event.from_user.id}")
        try:
            budgets = context['budgets']
            entity_list = await RequestManager().fetch_and_attach_entity_info(
                budgets,
                field_name='category_id',
                api_path_template='settings/categories/set',
                state=state
            )
            if entity_list is not None:
                entity_map = {entity['id']: entity for entity in entity_list}
                for budget in budgets:
                    entity_id = budget.get('category_id')
                    if entity_id and entity_id in entity_map:
                        budget['category'] = entity_map[entity_id]

            return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except RequestError as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при обновлении информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при получении информации о бюджетах пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class GetSubcategoryInfoForBudgetsHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о под-категориях бюджетов авторизированного пользователя {event.from_user.id}")
        try:
            budgets = context['budgets']
            entity_list = await RequestManager().fetch_and_attach_entity_info(
                budgets,
                field_name='subcategory_id',
                api_path_template='settings/subcategory/set',
                state=state
            )
            if entity_list is not None:
                entity_map = {entity['id']: entity for entity in entity_list }
                for budget in budgets:
                    entity_id = budget.get('subcategory_id')
                    if entity_id and entity_id in entity_map:
                        budget['subcategory'] = entity_map[entity_id]

            return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except RequestError as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при обновлении информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при получении информации о бюджетах пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class GetUserCashboxInfoForBudgetsHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о кэш-боксах бюджетов авторизированного пользователя {event.from_user.id}")
        try:
            budgets = context['budgets']
            entity_list = await RequestManager().fetch_and_attach_entity_info(
                budgets,
                field_name='user_cashbox_id',
                api_path_template='auth/me/cashboxes/set',
                state=state
            )
            if entity_list is not None:
                entity_map = {entity['id']: entity for entity in entity_list}
                for budget in budgets:
                    entity_id = budget.get('user_cashbox_id')
                    if entity_id and entity_id in entity_map:
                        budget['user_cashbox'] = entity_map[entity_id]

            return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except RequestError as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при обновлении информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при получении информации о бюджетах пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class CheckUserBudgetsAdditionalInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(
            f"[{self.__class__.__name__}] Проверка дополнительной информации о бюджетах авторизированного пользователя {event.from_user.id}")
        try:
            budgets = context['budgets']
            if any(
                    budget.get('category') is None and
                    budget.get('subcategory') is None and
                    budget.get('user_cashbox') is None
                    for budget in budgets
            ):
                await event.message.edit_text(text='Произошла критическая ошибка при работе с вашим бюджетом!\n\nПопробуйте позже или обратитесь в поддержку!',
                                              reply_markup=BudgetKeyboard().get_empty_budgets_menu_keyboard())
            else:
                await state.update_data(budgets=budgets)
                return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except RequestError as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при обновлении информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class ShowUserBudgetsHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(
            f"[{self.__class__.__name__}] Демонстрация пользовательских бюджетов авторизированного пользователя {event.from_user.id}")
        try:
            await state.set_state(BudgetState.choosing_budget_item)

            data = await state.get_data()
            budgets = data.get('budgets')

            index = data.get("budget_index", 0)
            budget = budgets[index]

            await event.message.edit_text(self._format_budget(budget, index, len(budgets)),
                                          reply_markup=BudgetKeyboard().get_user_budgets_menu_keyboard(),
                                          parse_mode='HTML')
            return True
        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

    def _format_budget(self, budget: dict, index: int, total: int) -> str:
        category = budget.get("category", {})
        subcategory = budget.get("subcategory", {})
        user_cashbox = budget.get("user_cashbox", {})
        user = budget.get("user", {})

        return (
            f"📊 <b>Бюджет</b> {index + 1}/{total}\n\n"
            f"🗂️ <b>Категория:</b> {(category.get('name', '—'))}\n"
            f"📁 <b>Подкатегория:</b> {(subcategory.get('name', '—'))}\n"
            f"💼 <b>Кэшбокс:</b> {(user_cashbox.get('custom_name') or user_cashbox.get('name', '—'))}\n"
            f"📅 <b>Месяц:</b> {budget.get('month')}.{budget.get('year')}\n"
            f"💰 <b>Сумма:</b> {budget.get('amount')} {(budget.get('currency', '—'))}\n"
            f"🔁 <b>Повторяется:</b> {'Да' if budget.get('is_recurring') else 'Нет'}\n"
            f"🔒 <b>Заблокирован:</b> {'Да' if budget.get('is_locked') else 'Нет'}\n"
            f"✏️ <b>Комментарий:</b> {(budget.get('comment', '—'))}\n"
            f"👤 <b>Пользователь:</b> {(user.get('first_name', ''))} {(user.get('last_name', ''))} (@{user.get('username', '—')})"
        )


class  CheckChosenBudgetHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Проверка выбранного бюджета авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            budgets = data.get('budgets')

            index = data.get("budget_index", 0)
            budget = budgets[index]

            if context is None:
                context = {}
            context['budget'] = budget

            if budget['id']:
                return await super().handle(event, state, context)
            else:
                Exception('чето не так')
        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class GetDetailBudgetInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение выбранного бюджета авторизированного пользователя {event.from_user.id}")
        try:
            budget = context['budgets']
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url=f'budget/{budget["id"]}', state=state)
            context["detail_budget"] = data
            return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except RequestError as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при обновлении информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class ShowDetailBudgetInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(
            f"[{self.__class__.__name__}] Демонстрация (детально) бюджета авторизированного пользователя {event.from_user.id}")
        try:
            budget = context["detail_budget"]
            await event.message.edit_text(self._format_budget(budget, index, len(budgets)),
                                          reply_markup=BudgetKeyboard().get_user_budgets_menu_keyboard(),
                                          parse_mode='HTML')
            return True
        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


    def _format_budget(self, budget: dict, index: int, total: int) -> str:
        category = budget.get("category", {})
        subcategory = budget.get("subcategory", {})
        user_cashbox = budget.get("user_cashbox", {})
        user = budget.get("user", {})

        return (
            f"📊 <b>Бюджет</b> {index + 1}/{total}\n\n"
            f"🗂️ <b>Категория:</b> {(category.get('name', '—'))}\n"
            f"📁 <b>Подкатегория:</b> {(subcategory.get('name', '—'))}\n"
            f"💼 <b>Кэшбокс:</b> {(user_cashbox.get('custom_name') or user_cashbox.get('name', '—'))}\n"
            f"📅 <b>Месяц:</b> {budget.get('month')}.{budget.get('year')}\n"
            f"💰 <b>Сумма:</b> {budget.get('amount')} {(budget.get('currency', '—'))}\n"
            f"🔁 <b>Повторяется:</b> {'Да' if budget.get('is_recurring') else 'Нет'}\n"
            f"🔒 <b>Заблокирован:</b> {'Да' if budget.get('is_locked') else 'Нет'}\n"
            f"✏️ <b>Комментарий:</b> {(budget.get('comment', '—'))}\n"
            f"👤 <b>Пользователь:</b> {(user.get('first_name', ''))} {(user.get('last_name', ''))} (@{user.get('username', '—')})"
        )
