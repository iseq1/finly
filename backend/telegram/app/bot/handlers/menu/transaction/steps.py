import datetime
import math

import aiogram.types
from aiogram.fsm.context import FSMContext
from app.bot.handlers.base import BaseHandler
from app.bot.keyboards.transaction import TransactionKeyboard
from app.bot.states import TransactionState
from app.utils.request import RequestManager
from app.exceptions.request_exceptions import TokenStorageError, RequestError
from app.utils.logger import logger

class GetSelectTransactionTypeHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Меню выбор типа транзакции")
        try:
            await state.set_state(TransactionState.waiting_for_transaction_field)
            await event.message.edit_text(text='Выберите тип транзакции, с которой хотите продолжить работу:', reply_markup=TransactionKeyboard.get_select_transaction_type_keyboard())
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации меню выбора типа транзакции для авторизации пользователя: {e}")
            await event.message.edit_text("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class GetUserCashboxInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации пользовательских кэш-боксов авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url='auth/me/cashboxes', state=state)
            if context is None:
                context = {}
            context['user_cashboxes'] = data
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


class CheckUserCashboxesHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Проверка пользовательских кэш-боксов авторизированного пользователя {event.from_user.id}")
        try:
            user_cashboxes = context['user_cashboxes']
            if len(user_cashboxes) == 0:
                await event.message.edit_text(text='У вас пока нет ни единого пользовательского кэш-бокса!', reply_markup=TransactionKeyboard().get_empty_user_cashbox_menu_keyboard())
            else:
                await state.update_data(user_cashboxes=user_cashboxes)
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


class ShowUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Демонстрация пользовательских кэш-боксов авторизированного пользователя {event.from_user.id}")
        try:
            await state.set_state(TransactionState.waiting_for_transaction_user_cashbox)

            data = await state.get_data()
            user_cashboxes = data.get('user_cashboxes')

            index = data.get("user_cashbox_index", 0)
            cashbox = user_cashboxes[index]

            await event.message.edit_text(self._format_cashbox(cashbox, index, len(user_cashboxes)), reply_markup=TransactionKeyboard().get_user_cashbox_menu_keyboard(), parse_mode='MarkdownV2')
            return True
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

    def _format_cashbox(self, cashbox: dict, index: int, total: int) -> str:
        box = cashbox.get("cashbox", {})
        provider = box.get("provider", {})
        cashbox_type = box.get("type", {})

        def esc(text):
            """Экранирование спецсимволов MarkdownV2"""
            if not isinstance(text, str):
                text = str(text)
            return (
                text.replace('\\', '\\\\')
                .replace('.', '\\.')
                .replace('-', '\\-')
                .replace('(', '\\(')
                .replace(')', '\\)')
                .replace('[', '\\[')
                .replace(']', '\\]')
                .replace('{', '\\{')
                .replace('}', '\\}')
                .replace('!', '\\!')
                .replace('=', '\\=')
                .replace('+', '\\+')
                .replace('*', '\\*')
                .replace('_', '\\_')
                .replace('`', '\\`')
                .replace('>', '\\>')
                .replace('#', '\\#')
                .replace('|', '\\|')
                .replace('~', '\\~')
            )

        return (
            f"Для создания записи транзакции необходимо выбрать ваш пользовательский *{esc('кэш-бокс')}*\\.\n"
            f"Выберите один из ваших *{esc('кэш-боксов:')}*\n\n"
            f"💼 *Кэш\\-бокс {index + 1}/{total}*\n\n"
            f"🏷️ *Название:* {esc(box.get('name', '—'))}\n"
            f"🏢 *Провайдер:* {esc(provider.get('name', '—'))}\n"
            f"📦 *Тип:* {esc(cashbox_type.get('name', '—'))}\n"
            f"💰 *Баланс:* {esc(cashbox.get('balance', '0'))} {esc(box.get('currency', '—'))}\n"
            f"✏️ *Пользовательское имя:* {esc(cashbox.get('custom_name', '—'))}\n"
            f"🗒️ *Заметка:* {esc(cashbox.get('note', '—'))}"
        )


class RememberUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Сохранение пользовательского кэш-бокса для транзакции авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            user_cashboxes = data.get('user_cashboxes')
            index = data.get("user_cashbox_index", 0)
            cashbox = user_cashboxes[index]
            await state.update_data(user_cashboxes=cashbox)
            return await super().handle(event, state, context)
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class GetCategoryInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о категориях для авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            transaction_action = data.get('transaction_action')
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url=f'settings/categories?type={transaction_action["type"]}', state=state)
            if context is None:
                context = {}
            context['categories'] = data
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

class CheckCategoryHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Проверка категорий для авторизированного пользователя {event.from_user.id}")
        try:
            categories = context['categories']
            if len(categories) == 0:
                await event.message.edit_text(text='В системе не зарегистрирована ни одна категория!\nПопробуйте немного позже или обратитесь в поддержку',
                                              reply_markup=TransactionKeyboard().get_empty_category_menu_keyboard())
            else:
                await state.update_data(categories=categories)
                return await super().handle(event, state, context)

        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class ShowCategoriesHandler(BaseHandler):
    CATEGORIES_PER_PAGE = 6
    async def handle(self, event, state: FSMContext, context: dict = None):
        try:
            logger.debug(f"[{self.__class__.__name__}] Показ списка категорий")
            await state.set_state(TransactionState.waiting_for_transaction_category)

            data = await state.get_data()
            categories = data.get("categories", [])
            index = data.get("categories_index", 0)
            print(categories)
            print(len(categories))
            print(index)
            # Считаем страницы
            total_pages = math.ceil(len(categories) / self.CATEGORIES_PER_PAGE)
            page = index % total_pages

            # Выбираем категории для текущей страницы
            start = page * self.CATEGORIES_PER_PAGE
            end = start + self.CATEGORIES_PER_PAGE
            current_page_categories = categories[start:end]

            # Удаляем предыдущее сообщение
            try:
                await event.message.delete()
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение: {e}")

            # Генерируем клавиатуру
            keyboard = self._generate_keyboard(current_page_categories, total_pages, page)
            await event.message.answer("📂 Выберите категорию:", reply_markup=keyboard)
            return True
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Ошибка показа категорий: {e}")
            await event.message.answer("🚨 Ошибка показа категорий.")

    def _generate_keyboard(self, categories: list, total_pages: int, page: int):
        buttons = []
        row = []

        # Добавляем кнопки с названиями категорий
        for i, category in enumerate(categories):
            btn = TransactionKeyboard.get_category_button(text=category['name'], id=i)
            row.append(btn)
            if len(row) == 2:
                buttons.append(row)
                row = []

        # Дополняем пустыми кнопками при необходимости
        if row:
            while len(row) < 2:
                row.append(TransactionKeyboard.get_empty_category_button())
            buttons.append(row)

        # Пагинация
        buttons.append(TransactionKeyboard.get_category_menu_subkeyboard(page, total_pages))

        return TransactionKeyboard.get_category_menu_keyboard(buttons)


class RememberCategoryHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Сохранение категории для транзакции авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            categories = data.get('categories')
            index = data.get("categories_index", 0)
            category = categories[index]
            await state.update_data(category=category)
            if context is None:
                context = {}
            context['category_id'] = category['id']
            return await super().handle(event, state, context)
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class GetSubcategoryByCategoryInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о под-категориях для авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url=f'settings/subcategories?category_id={context["category_id"]}', state=state)
            if context is None:
                context = {}
            context['subcategories'] = data
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

class CheckSubcategoryHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Проверка под-категорий для авторизированного пользователя {event.from_user.id}")
        try:
            subcategories = context['subcategories']
            if len(subcategories) == 0:
                await event.message.edit_text(text='В системе не зарегистрирована ни одна под-категория для данной категории!\nПопробуйте немного позже или обратитесь в поддержку',
                                              reply_markup=TransactionKeyboard().get_empty_category_menu_keyboard())
            else:
                await state.update_data(subcategories=subcategories)
                return await super().handle(event, state, context)

        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class ShowSubcategoriesHandler(BaseHandler):
    SUBCATEGORIES_PER_PAGE = 6
    async def handle(self, event, state: FSMContext, context: dict = None):
        try:
            logger.debug(f"[{self.__class__.__name__}] Показ списка под-категорий")
            await state.set_state(TransactionState.waiting_for_transaction_subcategory)

            data = await state.get_data()
            categories = data.get("subcategories", [])
            index = data.get("subcategories_index", 0)

            # Считаем страницы
            total_pages = math.ceil(len(categories) / self.SUBCATEGORIES_PER_PAGE)
            page = index % total_pages

            # Выбираем категории для текущей страницы
            start = page * self.SUBCATEGORIES_PER_PAGE
            end = start + self.SUBCATEGORIES_PER_PAGE
            current_page_categories = categories[start:end]

            # Удаляем предыдущее сообщение
            try:
                await event.message.delete()
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение: {e}")

            # Генерируем клавиатуру
            keyboard = self._generate_keyboard(current_page_categories, total_pages, page)
            await event.message.answer("📂 Выберите под-категорию:", reply_markup=keyboard)
            return True
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Ошибка показа категорий: {e}")
            await event.message.answer("🚨 Ошибка показа категорий.")

    def _generate_keyboard(self, subcategories: list, total_pages: int, page: int):
        buttons = []
        row = []

        # Добавляем кнопки с названиями категорий
        for i, subcategory in enumerate(subcategories):
            btn = TransactionKeyboard.get_subcategory_button(text=subcategory['name'], id=i)
            row.append(btn)
            if len(row) == 2:
                buttons.append(row)
                row = []

        # Дополняем пустыми кнопками при необходимости
        if row:
            while len(row) < 2:
                row.append(TransactionKeyboard.get_empty_category_button())
            buttons.append(row)

        # Пагинация
        buttons.append(TransactionKeyboard.get_subcategory_menu_subkeyboard(page, total_pages))

        return TransactionKeyboard.get_subcategory_menu_keyboard(buttons)


class RememberSubcategoryHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Сохранение под-категории для транзакции авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            subcategories = data.get('subcategories')
            index = data.get("subcategories_index", 0)
            print(subcategories)
            print(len(subcategories))
            print(index)
            subcategory = subcategories[index]
            await state.update_data(subcategory=subcategory)
            return await super().handle(event, state, context)
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class TakingTransactionInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о транзакции авторизированного пользователя {event.from_user.id}")
        try:
            await state.set_state(TransactionState.waiting_for_transaction_info)
            data = await state.get_data()
            # print(data)
            transaction_action = data.get('transaction_action').get('type')
            user_cashbox = data.get('user_cashboxes')
            category = data.get('category')
            subcategory = data.get('subcategory')
            new_user_transaction = data.get('new_user_transaction', {})

            if isinstance(event, aiogram.types.Message):
                if transaction_action == 'income':
                    await event.answer(
                        self._format_cashbox('income', user_cashbox, category, subcategory, new_user_transaction),
                        reply_markup=TransactionKeyboard.get_new_income_keyboard() if len(new_user_transaction.items()) != 4 else TransactionKeyboard.get_done_new_income_keyboard(), parse_mode='MarkdownV2')
                    return True
                elif transaction_action == 'expense':
                    await event.answer(self._format_cashbox('expense', user_cashbox, category, subcategory, new_user_transaction),
                                                  reply_markup=TransactionKeyboard.get_new_expense_keyboard() if len(new_user_transaction.items()) != 5 else TransactionKeyboard.get_new_done_expense_keyboard(),
                                                  parse_mode='MarkdownV2')
                    return True
                else:
                    pass

            if transaction_action=='income':
                await event.message.edit_text(self._format_cashbox('income', user_cashbox, category, subcategory, new_user_transaction),
                                   reply_markup=TransactionKeyboard.get_new_income_keyboard() if len(new_user_transaction.items()) != 4 else TransactionKeyboard.get_done_new_income_keyboard(), parse_mode='MarkdownV2')
                return True
            elif transaction_action=='expense':
                await event.message.edit_text(self._format_cashbox('expense', user_cashbox, category, subcategory, new_user_transaction),
                                              reply_markup=TransactionKeyboard.get_new_expense_keyboard() if len(new_user_transaction.items()) != 5 else TransactionKeyboard.get_new_done_expense_keyboard(), parse_mode='MarkdownV2')
                return True
            else:
                pass
        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при получении информации о новом пользовательском кэш-боксе: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

    def _format_cashbox(self, trans_type: str, user_cashbox: dict, category: dict, subcategory: dict, transaction_info: dict) -> str:
        cashbox = user_cashbox.get('cashbox')
        provider = cashbox.get('provider')
        type = cashbox.get('type')

        def esc(text):
            """Экранирование спецсимволов MarkdownV2"""
            if not isinstance(text, str):
                text = str(text)
            return (
                text.replace('\\', '\\\\')
                .replace('.', '\\.')
                .replace('-', '\\-')
                .replace('(', '\\(')
                .replace(')', '\\)')
                .replace('[', '\\[')
                .replace(']', '\\]')
                .replace('{', '\\{')
                .replace('}', '\\}')
                .replace('!', '\\!')
                .replace('=', '\\=')
                .replace('+', '\\+')
                .replace('*', '\\*')
                .replace('_', '\\_')
                .replace('`', '\\`')
                .replace('>', '\\>')
                .replace('#', '\\#')
                .replace('|', '\\|')
                .replace('~', '\\~')
            )

        def generate_message(trans_type):
            if trans_type=='income':
                return (
                    f"Мы уже почти сформировали запись о вашей транзакции\\, осталось лишь внести некоторые данные\\!\n\n"
                    f"Ваша новая транзакция\\:\n\n"
                    f"✏️ *Тип:* доход\n"
                    f"📦 *Кэш\\-бокс:* {esc(cashbox.get('name'))} \\({esc(type.get('name'))}\\) от {esc(provider.get('name'))}\n"
                    f"💰 *Текущее состояние баланса:* {esc(user_cashbox.get('balance'))} {esc(cashbox.get('currency'))}\n"
                    f"💰 *Выбранная категория:* {esc(category.get('name'))}\n"
                    f"💰 *Выбранная под\\-категория:* {esc(subcategory.get('name'))}\n"
                    f"*Сумма транзакции*: {esc(transaction_info.get('amount', '—'))} {esc(cashbox.get('currency'))}\n"
                    f"*Дата и время*: {esc(transaction_info.get('datetime', '—'))}\n"
                    f"*Комментарий*: {esc(transaction_info.get('comment', '—'))}\n"
                    f"*Источник дохода*: {esc(transaction_info.get('source', '—'))}\n"
                )
            elif trans_type=='expense':
                return (
                    f"Мы уже почти сформировали запись о вашей транзакции\\, осталось лишь внести некоторые данные\\!\n\n"
                    f"Ваша новая транзакция\\:\n\n"
                    f"✏️ *Тип:* доход\n"
                    f"📦 *Кэш\\-бокс:* {esc(cashbox.get('name'))} \\({esc(type.get('name'))}\\) от {esc(provider.get('name'))}\n"
                    f"💰 *Текущее состояние баланса:* {esc(user_cashbox.get('balance'))} {esc(cashbox.get('currency'))}\n"
                    f"💰 *Выбранная категория:* {esc(category.get('name'))}\n"
                    f"💰 *Выбранная под\\-категория:* {esc(subcategory.get('name'))}\n"
                    f"*Сумма транзакции*: {esc(transaction_info.get('amount', '—'))} {esc(cashbox.get('currency'))}\n"
                    f"*Дата и время*: {esc(transaction_info.get('datetime', '—'))}\n"
                    f"*Комментарий*: {esc(transaction_info.get('comment', '—'))}\n"
                    f"*Адресат транзакции*: {esc(transaction_info.get('vendor', '—'))}\n"
                    f"*Локация*: {esc(transaction_info.get('location', '—'))}\n"
                )
            else:
                pass


        return generate_message(trans_type)


class WaitTransactionFieldHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Ожидание информации о транзакции авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            field = data.get('get_transaction_field')
            if field == 'amount':
                await state.set_state(TransactionState.waiting_for_amount)
                await event.message.edit_text(f'Введите сумму транзакции!\nБудьте внимательны, т.к. основная валюта выбранного вами кэш-бокса - {data.get("user_cashboxes").get("cashbox").get("currency")}')
                return True
            elif field == 'comment':
                await state.set_state(TransactionState.waiting_for_comment)
                await event.message.edit_text(f'Введите комментарий к транзакции.')
                return True
            elif field == 'datetime':
                await state.set_state(TransactionState.waiting_for_datetime)
                await event.message.edit_text(f'Введите дату и время транзакции.\nФормат даты: ДД.ММ.ГГГГ\nФормат времени: ЧЧ:ММ (если не укажите время - установим время транзакции сами)\nФормат вашего ответа: ДД.ММ.ГГГГ ЧЧ.ММ')
                return True
            elif field == 'source':
                await state.set_state(TransactionState.waiting_for_source)
                await event.message.edit_text(f'Введите источник транзакции')
                return True
            elif field == 'location':
                await state.set_state(TransactionState.waiting_for_location)
                await event.message.edit_text(f'Введите ваше местоположение, где была совершена транзакция (на ваше усмотрение).')
                return True
            elif field == 'vendor':
                await state.set_state(TransactionState.waiting_for_vendor)
                await event.message.edit_text(f'Введите адресата транзакции')
                return True
            else:
                Exception('Неопознанное поле ввода')

        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при получении информации о новом пользовательском кэш-боксе: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class TakingTransactionFieldHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации об поле транзакции авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            get_transaction_field = data.get('get_transaction_field')
            from app.utils.profile import ValidateUserInput
            field = event.text.strip()
            success, ref = ValidateUserInput().validate_field(type=get_transaction_field, field=field)
            if not success:
                logger.error(f"[{self.__class__.__name__}] Ошибка пользовательского ввода")
                raise ref
            data = await state.get_data()
            new_user_transaction = data.get('new_user_transaction', {})
            new_user_transaction[f'{get_transaction_field}'] = ref
            await state.update_data(new_user_transaction=new_user_transaction)
            return await super().handle(event, state, context)

        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при получении информации о новом пользовательском кэш-боксе: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class CheckTransactionInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Проверка информации транзакции авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            transaction_type = data.get('transaction_action').get('type')
            new_user_transaction = data.get('new_user_transaction')
            if (len(new_user_transaction.items()) == 4 and transaction_type == 'income') or (len(new_user_transaction.items()) == 5 and transaction_type == 'expense'):
                return await super().handle(event, state, context)
            else:
                return Exception("Что-то не так с пользовательскими данными")

        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при получении информации о новом пользовательском кэш-боксе: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class MakeTransactionDataHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Создание json`а для запроса")
        try:
            data = await state.get_data()
            transaction_type = data.get('transaction_action').get('type')
            user_cashbox = data.get('user_cashboxes')
            category = data.get('category')
            subcategory = data.get('subcategory')
            new_user_transaction = data.get('new_user_transaction', {})

            if context is None:
                context = {}

            if transaction_type == 'income':
                context['json'] = {
                  "user_cashbox_id": user_cashbox.get('id'),
                  "category_id": category.get('id'),
                  "subcategory_id": subcategory.get('id'),
                  "amount": new_user_transaction.get('amount'),
                  "comment": new_user_transaction.get('comment'),
                  "transacted_at": new_user_transaction.get('datetime'),
                  "source": new_user_transaction.get('source'),
                }
                return await super().handle(event, state, context)
            elif transaction_type == 'expense':
                context['json'] = {
                  "user_cashbox_id": user_cashbox.get('id'),
                  "category_id": category.get('id'),
                  "subcategory_id": subcategory.get('id'),
                  "amount": new_user_transaction.get('amount'),
                  "comment": new_user_transaction.get('comment'),
                  "transacted_at": new_user_transaction.get('datetime'),
                  "vendor": new_user_transaction.get('vendor'),
                  "location": new_user_transaction.get('location')
                }
                return await super().handle(event, state, context)
            else:
                return Exception("Что-то не так с пользовательскими данными")

        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при получении информации о новом пользовательском кэш-боксе: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class SaveNewTransactionHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(
            f"[{self.__class__.__name__}] Сохранение информации пользовательских кэш-боксов авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            request_manager = RequestManager()
            data = await request_manager.make_request(method='POST', url=f'transactions/{data.get("transaction_action").get("type")}', state=state, json=context['json'])
            if context is None:
                context = {}
            context['transaction'] = data
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

class NotifySuccessesTransactionHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(
            f"[{self.__class__.__name__}] Уведомление пользователя об успехе {event.from_user.id}")
        try:
            event.message.edit_text('Транзакция успешно сохранена!', reply_markup=TransactionKeyboard.get_back_transaction_menu_keyboard())
            return await super().handle(event, state, context)
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class GetUserLatestTransactionInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение истории об последних транзакциях {event.from_user.id}")
        try:
            data = await state.get_data()
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url=f'transactions/{data.get("transaction_action").get("type")}?page=1&per_page=10&sort_by=id&sort_dir=desc', state=state)
            if context is None:
                context = {}
            context['transactions'] = data
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

class CheckUserLatestTransactionsInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Проверка истории об последних транзакциях {event.from_user.id}")
        try:
            if len(context['transactions']) == 0:
                event.message.edit_text(text='Кажется, у вас пока ещё нет ни одной записанной транзакции за этот месяц. Самое время записать их!', reply_markup=TransactionKeyboard.def_get_history_menu_keyboard())
            else:
                return await super().handle(event, state, context)
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class ShowUserLatestTransactionInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Демонстрация истории последних транзакций авторизированного пользователя {event.from_user.id}")
        try:
            await event.message.edit_text(f"📊 История последних доходов:\n\n{(self._format_history(context['transactions']))}", parse_mode="HTML", reply_markup=TransactionKeyboard.def_get_history_menu_keyboard())
            return True
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

    def _format_history(self, transactions: dict) -> str:
        lines = []
        print(transactions)
        for t in transactions['items']:
            lines.append(
                f"🧾 ID: {t['id']}\n"
                f"🏦 Кэш-бокс: {t['user_cashbox']['cashbox']['name']}\n"
                f"📂 Категория: {t['category']['name']}\n"
                f"📁 Подкатегория: {t['subcategory']['name']}\n"
                f"📅 Дата: {t['transacted_at'][:10]}\n"
                f"💰 Сумма: {t['amount']} {t['user_cashbox']['cashbox']['currency']}\n"
                f"|----------|----------|----------|\n"
            )
        return "\n".join(lines)

class GetUserTransactionStatisticHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение статистики авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url=f'transactions/statistics?type={data.get("transaction_action").get("type")}&include_empty_categories=False', state=state)
            if context is None:
                context = {}
            context['statistic'] = data
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

class CheckUserTransactionStatisticHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Проверка наличия статистики авторизированного пользователя {event.from_user.id}")
        try:
            if len(context['statistic']) == 0:
                event.message.edit_text(text='Кажется, у вас пока ещё нет ни одной записанной транзакции за этот месяц. Самое время записать их!', reply_markup=TransactionKeyboard.def_get_history_menu_keyboard())
            else:
                return await super().handle(event, state, context)
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class ShowUserTransactionStatisticHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Демонстрация статистики транзакций авторизированного пользователя {event.from_user.id}")
        try:
            print(context['statistic'])
            await event.message.edit_text(f"{(self._format_stat(context['statistic']))}", parse_mode="HTML", reply_markup=TransactionKeyboard.get_statistic_menu_keyboard())
            return True
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

    def _format_stat(self, transactions: dict) -> str:
        lines = ["📊 <b>Статистика транзакций</b>\n"]

        # Перебираем категории
        for category_name, category_data in transactions['statistics'].items():
            total = transactions['category_totals'].get(category_name, 0)
            lines.append(f"📂 <b>{category_name}</b>: {round(total, 2)}₽")

            # Перебираем провайдеров внутри категории
            providers = category_data.get('data', {})
            for provider_name, provider_data in providers.items():
                amount = provider_data.get('sum', 0)
                currency = provider_data.get('currency', 0)
                if amount > 0:
                    lines.append(f"    └ 🏦 {provider_name}: {round(amount, 2)} {currency}")

            lines.append("")  # Пустая строка между категориями

        # Итоги по провайдерам
        lines.append("<b>💼 Итоги по провайдерам:</b>")
        for provider_name, amount in transactions.get('provider_totals', {}).items():
            lines.append(f"🏦 {provider_name}: {round(amount, 2)}")

        return "\n".join(lines)
