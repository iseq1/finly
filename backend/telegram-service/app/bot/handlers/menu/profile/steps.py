import datetime
import aiogram.types
from aiogram.fsm.context import FSMContext
from app.bot.handlers.base import BaseHandler
from app.bot.keyboards.profile import ProfileKeyboard
from app.bot.states import EditProfileState, CreateNewUserCashbox
from app.utils.request import RequestManager
from app.exceptions.profile_exceptions import ProfileError, ProfileInfoUnavailable
from app.exceptions.request_exceptions import TokenStorageError, RequestError
from app.utils.logger import logger
from app.utils.image_convertor import img_convertor


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
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
        except RequestError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при получении информации профиля пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.message.edit_text("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class GetUserCashboxesHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о количестве кэш-боксов авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url='auth/me/cashboxes', state=state)
            context['user_cashboxes_count'] = len(data)

            return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
        except RequestError as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при получении информации о количестве кэш-боксов пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.message.edit_text("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class GetUserBudgetHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о количестве бюджетов авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url='budget', state=state)
            context['user_budgets_count'] = len(data)
            return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
        except RequestError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при получении информации о количестве бюджетов пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.message.edit_text("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class GetUserTransactionsHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о количестве транзакциях авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            income_data = await request_manager.make_request(method='GET', url='transactions/income', state=state)
            expense_data = await request_manager.make_request(method='GET', url='transactions/expense', state=state)
            context['user_transactions_count'] = len(income_data) + len(expense_data)
            return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
        except RequestError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при получении информации о количестве транзакций пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.message.edit_text("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class GenerateProfileMessageHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Генерация профиля авторизированного пользователя {event.from_user.id}")
        from datetime import datetime
        try:
            profile_data = context['user_update_data']['user'] if context.get('user_update_data', False) else context['user_data']
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
                f"✅ Активен: {'Да' if profile_data['is_active'] else 'Нет'}\n"
                f"🕒 Последний вход: {last_login}\n\n"
                f"💰 Количество кэш-боксов: {cashboxes}\n"
                f"📊 Количество бюджетов на месяц: {budgets}\n"
                f"💸 Количество транзакций за месяц: {transactions}\n"
            )

            context['profile_message'] = message
            return await super().handle(event, state, context)

        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
        except RequestError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при генерации профиля пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.message.edit_text("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


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
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
        except RequestError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при открытии меню изменения личной информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.message.edit_text("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class WaitNewFieldHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Ожидание данных для обновления информации авторизированного пользователя {event.from_user.id}")
        try:
            await state.set_state(EditProfileState.waiting_for_value)
            await state.update_data(chain_step=8)

            data = await state.get_data()
            await event.message.edit_text(f"Введите новое значение для поля: {data['field_to_edit']}")

            return False
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
        except RequestError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при обновлении информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.message.edit_text("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class TakingNewFieldHandler(BaseHandler):

    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение данных для обновления информации авторизированного пользователя {event.from_user.id}")
        try:
            from app.utils.profile import ValidateUserInput
            field = event.text.strip()

            data = await state.get_data()
            field_to_edit = data['field_to_edit']

            success, ref = ValidateUserInput().validate_field(type=field_to_edit, field=field)

            if not success:
                logger.error(f"[{self.__class__.__name__}] Ошибка пользовательского ввода")
                raise ref

            await state.update_data(new_field=ref)
            return await super().handle(event, state, context)

        except ValueError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка пользовательского ввода")
            await event.answer(f'{e}\n\nПопробуйте ещё раз!')
            return False
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except RequestError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при обновлении информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class MakeDataDictHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Создание JSON для апдейта данных")
        try:
            data = await state.get_data()
            field_to_edit = data['field_to_edit']
            new_field = data['new_field']
            request_manager = RequestManager()
            user_data = await request_manager.make_request(method='GET', url='auth/me', state=state)
            update_data = {
                "username": user_data['username'],
                "email": user_data['email'],
                "first_name": user_data['first_name'],
                "last_name": user_data['last_name'],
                "patronymic": user_data['patronymic'],
                "phone_number": user_data['phone_number'],
                "birthday": user_data['birthday'],
            }
            update_data[field_to_edit] = new_field

            context['json_to_update'] = update_data

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


class EditProfileInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Обновление данных авторизированного пользователя {event.from_user.id}")
        try:

            request_manager = RequestManager()
            user_update_data = await request_manager.make_request(method='PUT', url='auth/me', state=state, json=context['json_to_update'])
            context = user_update_data
            return await super().handle(event, state, context)

            # TODO: delete trash from state in the end + in the exit button (need only access, refresh, userid)

        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except RequestError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при обновлении информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class NotifyUpdateSuccessHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        try:
            if context['message'] == 'Профиль успешно обновлен':
                await event.answer(text='Данные вашего профиля успешно обновлены!', reply_markup=ProfileKeyboard().get_back_profile_menu_keyboard())
                return False
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except RequestError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при обновлении информации пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class GetUserCashboxInfo(BaseHandler):
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
                await event.message.edit_text(text='У вас пока нет ни единого пользовательского кэш-бокса!', reply_markup=ProfileKeyboard().get_empty_user_cashbox_menu_keyboard())
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


class ShowUserCashbox(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Демонстрация пользовательских кэш-боксов авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            user_cashboxes = data.get('user_cashboxes')

            index = data.get("user_cashbox_index", 0)
            cashbox = user_cashboxes[index]

            await event.message.edit_text(self._format_cashbox(cashbox, index, len(user_cashboxes)), reply_markup=ProfileKeyboard().get_more_action_user_cashbox_keyboard() if data.get('user_cashbox_details', False) else ProfileKeyboard().get_user_cashbox_menu_keyboard(), parse_mode='MarkdownV2')
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
            f"💼 *Кэш\\-бокс {index + 1}/{total}*\n\n"
            f"🏷️ *Название:* {esc(box.get('name', '—'))}\n"
            f"🏢 *Провайдер:* {esc(provider.get('name', '—'))}\n"
            f"📦 *Тип:* {esc(cashbox_type.get('name', '—'))}\n"
            f"💰 *Баланс:* {esc(cashbox.get('balance', '0'))} {esc(box.get('currency', '—'))}\n"
            f"✏️ *Пользовательское имя:* {esc(cashbox.get('custom_name', '—'))}\n"
            f"🗒️ *Заметка:* {esc(cashbox.get('note', '—'))}"
        )


class GetProviderInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение списка провайдеров кэш-боксов для авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url='settings/cashboxes-provider', state=state)
            if context is None:
                context = {}
            context['cashbox_providers'] = data
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


class CheckCashboxProvidersHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Проверка провайдеров кэш-боксов")
        try:
            cashbox_providers = context['cashbox_providers']
            if len(cashbox_providers) == 0:
                await event.message.edit_text(text='В системе пока не зарегистрировано ни одного кэш-бокса!\nЖдём вас позже <3', reply_markup=ProfileKeyboard().get_back_profile_menu_keyboard())
            else:
                await state.update_data(cashbox_providers=cashbox_providers)
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



class ShowCashboxProvidersHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Демонстрация провайдеров кэш-боксов для авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            cashbox_providers = data.get('cashbox_providers')

            index = data.get("cashbox_providers_index", 0)
            provider = cashbox_providers[index]
            await event.message.delete()
            provider_logo = provider.get('logo_url')
            await event.message.answer_photo(
                photo=provider_logo if not str(provider_logo).startswith('data:') else img_convertor(provider_logo),
                reply_markup=ProfileKeyboard().get_provider_cashbox_menu_keyboard(provider.get('name', None))
            )
            return True
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации провайдеров кэш-боксов пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class ClearAfterProvidersHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Возвращение в меню профиля авторизированного пользователя {event.from_user.id}")
        try:
            await event.message.delete()
            await event.message.answer(text='Меню профиля:', reply_markup=ProfileKeyboard.get_profile_menu_keyboard())
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при возвращении в меню профиля пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class TakingProviderInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Обработка выбора провайдера кэш-боксов авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            cashbox_providers = data.get("cashbox_providers", [])
            index = (data.get("cashbox_providers_index", 0)) % len(cashbox_providers)
            if context is None:
                context = {}
            context['provider'] = cashbox_providers[index]
            return await super().handle(event, state, context)
        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при обработке выбора провайдера кэш-боксов авторизированного пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class GetCashboxesByProvider(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение кэш-боксов по провайдеру для авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            data = await request_manager.make_request(method='GET', url=f'settings/cashboxes?provider_id={(context["provider"]).get("id")}', state=state)
            context['cashboxes_by_provider'] = data
            return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except RequestError as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при получении кэш-боксов по провайдеру для пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.answer(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при получении кэш-боксов по провайдеру пользователя: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class CheckCashboxesByProviderHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Проверка кэш-боксов по провайдеру для авторизированного пользователя {event.from_user.id}")
        try:
            if context['cashboxes_by_provider'] and len(context['cashboxes_by_provider'])!=0:
                await state.update_data(cashboxes_by_provider=context['cashboxes_by_provider'])
                return await super().handle(event, state, context)
            else:
                await event.message.delete()
                await event.message.edit_text(text='В системе пока не зарегистрировано ни одного кэш-бокса от данного провайдера!\nЖдём вас позже <3', reply_markup=ProfileKeyboard().get_back_profile_menu_keyboard())
                return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при проверке кэш-боксов по провайдеру: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class ShowCashboxesByProviderHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Демонстрация кэш-боксов по провайдеру для авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            cashboxes_by_provider = data.get('cashboxes_by_provider')
            index = data.get("cashbox_by_provider_index", 0)
            cashbox = cashboxes_by_provider['items'][index]
            print(cashbox)
            await event.message.delete()
            await event.message.answer(self._format_cashbox(cashbox, index, len(cashboxes_by_provider['items'])), reply_markup=ProfileKeyboard().get_cashboxes_by_provider_menu_keyboard(), parse_mode='MarkdownV2')
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов по провайдеру: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

    def _format_cashbox(self, cashbox: dict, index: int, total: int) -> str:
        provider = cashbox.get("provider", {})
        cashbox_type = cashbox.get("type", {})

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
            f"💼 *Кэш\\-бокс {index + 1}/{total}*\n\n"
            f"🏷️ *Название:* {esc(cashbox.get('name', '—'))}\n"
            f"🏢 *Провайдер:* {esc(provider.get('name', '—'))}\n"
            f"📦 *Тип:* {esc(cashbox_type.get('name', '—'))}\n"
            f"💰 *Валюта:* {esc(cashbox.get('currency', '—'))}\n"
            f"✏️ *Описание:* {esc(cashbox.get('description', '—'))}\n"

        )


class TakingNewUserCashboxInfoHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение информации о новом пользовательском кэш-боксе авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            cashboxes_by_provider = data.get('cashboxes_by_provider')
            index = data.get("cashbox_by_provider_index", 0)
            cashbox = cashboxes_by_provider['items'][index]
            new_user_cashbox = data.get('new_user_cashbox')
            if isinstance(event, aiogram.types.Message):
                await event.answer(self._format_cashbox(cashbox, new_user_cashbox), reply_markup=ProfileKeyboard().get_set_new_user_cashbox_keyboard(new_user_cashbox.get('is_auto_update', False)) if len(new_user_cashbox.items()) < 4 else ProfileKeyboard().get_set_done_new_user_cashbox_keyboard(new_user_cashbox.get('is_auto_update', False)), parse_mode='MarkdownV2')
                return True
            await event.message.edit_text(self._format_cashbox(cashbox, new_user_cashbox), reply_markup=ProfileKeyboard().get_set_new_user_cashbox_keyboard(new_user_cashbox.get('is_auto_update', False)) if len(new_user_cashbox.items()) < 4 else ProfileKeyboard().get_set_done_new_user_cashbox_keyboard(new_user_cashbox.get('is_auto_update', False)), parse_mode='MarkdownV2')
        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при получении информации о новом пользовательском кэш-боксе: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


    def _format_cashbox(self, cashbox: dict, new_user_cashbox: dict) -> str:
        provider = cashbox.get("provider", {})
        cashbox_type = cashbox.get("type", {})

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
            f"Вы выбрали *{esc(cashbox.get('name', '—'))}* от *{esc(provider.get('name', '—'))}*\n\n"
            f"✏️ *Описание:* {esc(cashbox.get('description', '—'))}\n"
            f"📦 *Тип:* {esc(cashbox_type.get('name', '—'))}\n"
            f"💰 *Валюта:* {esc(cashbox.get('currency', '—'))}\n\n"
            f"{esc('Теперь вы можете персонализировать данный кэш-бокс для дальнейшего использования при учете личных финансов!')}\n"
            f"Персонализация:\n\n"
            f"*Баланс*: {esc(new_user_cashbox.get('balance', '—'))}\n"
            f"*Кастомное имя*: {esc(new_user_cashbox.get('custom_name', '—'))}\n"
            f"*Примечание*: {esc(new_user_cashbox.get('note', '—'))}\n"
            f"*Автоматическое обновление*: {esc(new_user_cashbox.get('is_auto_update', '—'))}\n"

        )

class WaitBalanceUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение баланса нового пользовательского кэш-бокса авторизированного пользователя {event.from_user.id}")
        try:
            await state.set_state(CreateNewUserCashbox.waiting_for_balance)
            data = await state.get_data()
            cashboxes_by_provider = data.get('cashboxes_by_provider')
            index = data.get("cashbox_by_provider_index", 0)
            cashbox = cashboxes_by_provider['items'][index]
            await event.message.edit_text(text=f'Введите актуальный баланс кэш-бокса.\nБудьте внимательны, что валюта кэш-бокса подразумевает сумму в {cashbox.get("currency")}')
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов по провайдеру: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class WaitCustomNameUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение кастомного имени нового пользовательского кэш-бокса авторизированного пользователя {event.from_user.id}")
        try:
            await state.set_state(CreateNewUserCashbox.waiting_for_custom_name)
            await event.message.edit_text(text=f'Введите кастомное имя для кэш-бокса.')
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов по провайдеру: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class WaiNoteUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение заметки нового пользовательского кэш-бокса авторизированного пользователя {event.from_user.id}")
        try:
            await state.set_state(CreateNewUserCashbox.waiting_for_note)
            await event.message.edit_text(text=f'Введите заметку для кэш-бокса.')
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов по провайдеру: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class TakingNoteUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение заметки нового пользовательского кэш-бокса авторизированного пользователя {event.from_user.id}")
        try:
            from app.utils.profile import ValidateUserInput
            field = event.text.strip()
            field_to_edit = 'note'
            success, ref = ValidateUserInput().validate_field(type=field_to_edit, field=field)
            if not success:
                logger.error(f"[{self.__class__.__name__}] Ошибка пользовательского ввода")
                raise ref
            data = await state.get_data()
            new_user_cashbox = data.get('new_user_cashbox')
            new_user_cashbox['note'] = ref
            await state.update_data(new_user_cashbox=new_user_cashbox)
            return await super().handle(event, state, context)
        except ValueError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка пользовательского ввода")
            await event.answer(f'{e}\n\nПопробуйте ещё раз!')
            return False
        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов по провайдеру: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class TakingCustomNameUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение кастомного имени нового пользовательского кэш-бокса авторизированного пользователя {event.from_user.id}")
        try:
            from app.utils.profile import ValidateUserInput
            field = event.text.strip()
            field_to_edit = 'custom_name'
            success, ref = ValidateUserInput().validate_field(type=field_to_edit, field=field)
            if not success:
                logger.error(f"[{self.__class__.__name__}] Ошибка пользовательского ввода")
                raise ref
            data = await state.get_data()
            new_user_cashbox = data.get('new_user_cashbox')
            new_user_cashbox['custom_name'] = ref
            await state.update_data(new_user_cashbox=new_user_cashbox)
            return await super().handle(event, state, context)
        except ValueError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка пользовательского ввода")
            await event.answer(f'{e}\n\nПопробуйте ещё раз!')
            return False
        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов по провайдеру: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class TakingBalanceUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Получение баланса нового пользовательского кэш-бокса авторизированного пользователя {event.from_user.id}")
        try:
            from app.utils.profile import ValidateUserInput
            field = event.text.strip()

            field_to_edit = 'balance'
            success, ref = ValidateUserInput().validate_field(type=field_to_edit, field=field)

            if not success:
                logger.error(f"[{self.__class__.__name__}] Ошибка пользовательского ввода")
                raise ref

            data = await state.get_data()
            new_user_cashbox = data.get('new_user_cashbox')
            new_user_cashbox['balance'] = ref
            await state.update_data(new_user_cashbox=new_user_cashbox)
            return await super().handle(event, state, context)


        except ValueError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка пользовательского ввода")
            await event.answer(f'{e}\n\nПопробуйте ещё раз!')
            return False
        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов по провайдеру: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class GenerateNewUserCashboxDataHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Формирование json для нового пользовательского кэш-бокса авторизированного пользователя {event.from_user.id}")
        try:
            data = await state.get_data()
            new_user_cashbox = data.get('new_user_cashbox')
            cashboxes_by_provider = data.get('cashboxes_by_provider')
            index = data.get("cashbox_by_provider_index", 0)
            cashbox = cashboxes_by_provider['items'][index]

            post_data = {
              "user_id": data.get('user_id'),
              "cashbox_id": cashbox['id'],
              "balance": new_user_cashbox['balance'],
              "is_auto_update": new_user_cashbox['is_auto_update'],
              "last_synced_at": datetime.datetime.now().isoformat(),
              "custom_name": new_user_cashbox['custom_name'],
              "note": new_user_cashbox['note']
            }

            if context is None:
                context = {}
            context['post_data'] = post_data

            return await super().handle(event, state, context)
        except Exception as e:
            logger.exception(
                f"[{self.__class__.__name__}] Неизвестная ошибка при демонстрации кэш-боксов по провайдеру: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class PostNewUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Запрос на создание пользовательского кэш-бокса для авторизированного пользователя {event.from_user.id}")
        try:
            request_manager = RequestManager()
            data = await request_manager.make_request(method='POST', url='auth/me/cashboxes', state=state, json=context['post_data'])
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


class NotifyNewUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Запрос на создание пользовательского кэш-бокса для авторизированного пользователя {event.from_user.id}")
        try:
            await event.message.edit_text(text='Вы успешно создали новый пользовательский кэш-бокс!\n\nТеперь его можно использовать для учета движения ваших средств.', reply_markup=ProfileKeyboard.get_back_profile_menu_keyboard())
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


class ConfirmingDeletionUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Подтверждение удаления пользовательского кэш-бокса {event.from_user.id}")
        try:
            data = await state.get_data()
            user_cashboxes = data.get('user_cashboxes')
            index = data.get("user_cashbox_index", 0)
            cashbox = user_cashboxes[index]
            await event.message.edit_text(text=f'Вы уверены, что хотите удалить свой кэш-бокс ({cashbox.get("cashbox", {}).get("name", "—")})?', reply_markup=ProfileKeyboard.get_confirm_for_deletion_user_cashbox_keyboard())
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
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при удалении пользовательского кэш-бокса: {e}")
            await event.answer("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False


class DeleteUserCashboxesHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Удаление пользовательского к-б")
        try:
            data = await state.get_data()

            user_cashboxes = data.get('user_cashboxes')
            index = data.get("user_cashbox_index", 0)
            cashbox = user_cashboxes[index]
            request_manager = RequestManager()
            temp = await request_manager.make_request(method='DELETE', url=f'auth/me/cashboxes/{cashbox.get("id", "None")}', state=state)
            # Очистить стейт и оставить только нужные поля
            tokens = {
                'access_token': data.get('access_token'),
                'refresh_token': data.get('refresh_token'),
                'user_id': data.get('user_id'),
            }
            await state.clear()
            await state.update_data(**tokens)
            return await super().handle(event, state, context)
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
        except RequestError as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при получении информации о количестве кэш-боксов пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.message.edit_text("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False

class NotifyDeletionUserCashboxHandler(BaseHandler):
    async def handle(self, event, state: FSMContext, context: dict = None):
        logger.debug(f"[{self.__class__.__name__}] Оповещение об успешном удалении КБ")
        try:
            await event.message.edit_text(text=f'Пользовательский кэш-бокс успешно удален!', reply_markup=ProfileKeyboard.get_back_profile_menu_keyboard())
        except TokenStorageError as e:
            logger.error(f"[{self.__class__.__name__}] Ошибка при работе с токенами: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
        except RequestError as e:
            logger.error(
                f"[{self.__class__.__name__}] Ошибка при получении информации о количестве кэш-боксов пользователя: {event.from_user.id}")
            text, markup = e.to_user_message_with_markup()
            await event.message.edit_text(text, reply_markup=markup)
            return False
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Неизвестная ошибка при авторизации пользователя: {e}")
            await event.message.edit_text("🚨 Произошла непредвиденная ошибка. Попробуйте снова или позже.")
            return False
