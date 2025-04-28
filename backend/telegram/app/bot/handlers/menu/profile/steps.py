from aiogram.fsm.context import FSMContext
from app.bot.handlers.base import BaseHandler
from app.bot.keyboards.profile import ProfileKeyboard
from app.bot.states import EditProfileState
from app.utils.request import RequestManager
from app.utils.logger import logger


class GetProfileInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации профиля авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url='auth/me', state=state)

            if context is None:
                context = {}

            context['user_data'] = data

            return await super().handle(event, state, context)

        except Exception as e:
            pass


class GetUserCashboxesHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о количестве кэш-боксов авторизированного пользователя {event.from_user.id}")

        try:
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url='auth/me/cashboxes', state=state)
            context['user_cashboxes_count'] = len(data)

            return await super().handle(event, state, context)

        except Exception as e:
            pass


class GetUserBudgetHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о количестве бюджетов авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url='budget', state=state)
            context['user_budgets_count'] = len(data)

            return await super().handle(event, state, context)

        except Exception as e:
            pass


class GetUserTransactionsHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о количестве транзакциях авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            income_data = await request_manager.make_request(method='GET', url='transactions/income', state=state)
            expense_data = await request_manager.make_request(method='GET', url='transactions/expense', state=state)
            context['user_transactions_count'] = len(income_data) + len(expense_data)

            return await super().handle(event, state, context)

        except Exception as e:
            pass


class GenerateProfileMessageHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Генерация профиля авторизированного пользователя {event.from_user.id}")
        from datetime import datetime
        try:
            profile_data = context['user_data']
            birthday = datetime.fromisoformat(profile_data['birthday']).strftime('%d.%m.%Y')
            last_login = datetime.fromisoformat(profile_data['last_login']).strftime('%d.%m.%Y %H:%M')
            patronymic = profile_data.get('patronymic') or '(не указано)'
            cashboxes = context['user_cashboxes_count']
            budgets = context['user_budgets_count']
            transactions = context['user_transactions_count']

            message = (
                "👤 Профиль пользователя\n\n"
                f"🆔 ID: {profile_data['id']}\n"
                f"👤 Имя: {profile_data['first_name']}\n"
                f"👥 Фамилия: {profile_data['last_name']}\n"
                f"📛 Отчество: {patronymic}\n"
                f"📧 Email: {profile_data['email']}\n"
                f"📱 Телефон: {profile_data['phone_number']}\n"
                f"🎂 День рождения: {birthday}\n"
                f"📝 Логин в системе: {profile_data['username']}\n"
                f"💬 Telegram Username: @{profile_data['telegram_username']}\n"
                f"✅ Активен: {'Да' if profile_data['is_active'] else 'Нет'}\n"
                f"🕒 Последний вход: {last_login}\n\n"
                f"💰 Количество кэш-боксов: {cashboxes}\n"
                f"📊 Количество бюджетов на месяц: {budgets}\n"
                f"💸 Количество транзакций за месяц: {transactions}\n"
            )

            context['profile_message'] = message
            return await super().handle(event, state, context)

        except Exception as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при генерации профиля авторизированного пользователя {event.from_user.id}")
            pass

class SendProfileInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Демонстрация информации профиля авторизированного пользователя {event.from_user.id}")
        await state.update_data(profile_info=context['profile_message'])
        await state.set_state(EditProfileState.waiting_for_choosing_action)
        await state.update_data(chain_step=6)
        await event.message.edit_text(
            text=f"{context['profile_message']}",
            reply_markup=ProfileKeyboard.get_me_menu_keyboard()
        )
        return False


class GetChangeProfileHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Открытие меню изменений личный информации авторизированного пользователя {event.from_user.id}")
        try:
            await state.set_state(EditProfileState.choosing_field)
            await state.update_data(chain_step=7)

            data = await state.get_data()
            await event.message.edit_text(
                text=f"{data.get('profile_info')}",
                reply_markup=ProfileKeyboard.get_me_change_keyboard()
            )
            return False
        except Exception as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при открытии меню изменений личный информации авторизированного пользователя {event.from_user.id}")
            pass

class WaitNewFieldHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Ожидание данных для обновления информации авторизированного пользователя {event.from_user.id}")
        try:
            await state.set_state(EditProfileState.waiting_for_value)
            await state.update_data(chain_step=8)

            data = await state.get_data()
            await event.message.edit_text(f"Введите новое значение для поля: {data['field_to_edit']}")

            return False
        except Exception as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при ожидание данных для обновления информации авторизированного пользователя {event.from_user.id}")
            pass

class TakingNewFieldHandler(BaseHandler):

    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение данных для обновления информации авторизированного пользователя {event.from_user.id}")
        try:
            # TODO: validate per type
            field = event.text.strip()

            await state.update_data(new_field=field)
            return await super().handle(event, state, context)


        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при получении данных для обновления информации авторизированного пользователя {event.from_user.id}")
            pass


class EditProfileInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Обновление данных авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            print(data['field_to_edit'])
            print(data['new_field'])
            print('We ARE THERE DUDE')
            print(data)
            # TODO: PUT to server
            # TODO: delete trash from state in the end + in the exit button (need only access, refresh, userid)
            pass
        except Exception as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка обновление данных авторизированного пользователя {event.from_user.id}")
            pass