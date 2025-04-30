from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class ProfileKeyboard:

    @staticmethod
    def get_next_provider_cashbox_button():
        return InlineKeyboardButton(text='Следующий ▶️', callback_data="provider_cashbox_next")

    @staticmethod
    def get_previous_provider_cashbox_button():
        return InlineKeyboardButton(text='◀️ Предыдущий', callback_data="provider_cashbox_prev")

    @staticmethod
    def get_provider_cashbox_button(provider_name):
        return InlineKeyboardButton(text=provider_name, callback_data="get_provider")

    @staticmethod
    def get_create_user_cashbox_button():
        return InlineKeyboardButton(text='Создать новый кэш-бокс', callback_data='create_user_cashbox')

    @staticmethod
    def get_next_user_cashbox_button():
        return InlineKeyboardButton(text='Следующий ▶️', callback_data="user_cashbox_next")

    @staticmethod
    def get_previous_user_cashbox_button():
        return InlineKeyboardButton(text='◀️ Предыдущий', callback_data="user_cashbox_prev")

    @staticmethod
    def get_take_cashbox_by_provider_button():
        return InlineKeyboardButton(text='Выбрать', callback_data='cashbox_by_provider_take')

    @staticmethod
    def get_next_cashbox_by_provider_button():
        return InlineKeyboardButton(text='Следующий ▶️', callback_data="cashbox_by_provider_next")

    @staticmethod
    def get_previous_cashbox_by_provider_button():
        return InlineKeyboardButton(text='◀️ Предыдущий', callback_data="cashbox_by_provider_prev")

    @staticmethod
    def get_back_to_cashbox_provider_menu_button():
        return InlineKeyboardButton(text='Вернуться обратно', callback_data='create_user_cashbox')

    @staticmethod
    def get_change_user_cashbox_button():
        return InlineKeyboardButton(text='Изменить текущий кэш-бокс', callback_data="user_cashbox_edit")

    @staticmethod
    def get_delete_user_cashbox_button():
        return InlineKeyboardButton(text='Удалить текущий кэш-бокс', callback_data='user_cashbox_delete')

    @staticmethod
    def get_more_action_user_cashbox_button():
        return InlineKeyboardButton(text='Подробнее', callback_data='user_cashbox_details')

    @staticmethod
    def get_back_to_user_cashbox_button():
        return InlineKeyboardButton(text='Вернуться назад', callback_data='user_cashbox_back')

    @staticmethod
    def get_profile_menu_button():
        return InlineKeyboardButton(text='Профиль', callback_data='profile_menu')

    @staticmethod
    def get_change_profile_info_button():
        return InlineKeyboardButton(text='Обновить данные', callback_data='change_profile_info_menu')

    @staticmethod
    def get_back_to_profile_menu_button():
        return InlineKeyboardButton(text='Вернуться в меню профиля', callback_data='profile_menu')

    @staticmethod
    def get_back_to_profile_menu_from_providers_menu_button():
        return InlineKeyboardButton(text='Вернуться в меню профиля', callback_data='back_to_profile_menu_from_providers_menu')


    @staticmethod
    def get_change_first_name_button():
        return InlineKeyboardButton(text='Имя', callback_data='change_first_name')

    @staticmethod
    def get_change_last_name_button():
        return InlineKeyboardButton(text='Фамилия', callback_data='change_last_name')

    @staticmethod
    def get_change_patronymic_button():
        return InlineKeyboardButton(text='Отчество', callback_data='change_patronymic')

    @staticmethod
    def get_change_email_button():
        return InlineKeyboardButton(text='E-mail', callback_data='change_email')

    @staticmethod
    def get_change_phone_number_button():
        return InlineKeyboardButton(text='Телефон', callback_data='change_phone_number')

    @staticmethod
    def get_change_username_button():
        return InlineKeyboardButton(text='Логин в системе', callback_data='change_username')

    @staticmethod
    def get_change_birthday_button():
        return InlineKeyboardButton(text='День рождение', callback_data='change_birthday')

    @staticmethod
    def get_me_change_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    ProfileKeyboard.get_change_first_name_button(),
                    ProfileKeyboard.get_change_last_name_button(),
                    ProfileKeyboard.get_change_patronymic_button()
                ],
                [
                    ProfileKeyboard.get_change_birthday_button(),
                    ProfileKeyboard.get_change_phone_number_button()
                ],
                [
                    ProfileKeyboard.get_change_username_button(),
                    ProfileKeyboard.get_change_email_button()
                ],
                [
                    ProfileKeyboard.get_back_to_profile_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_me_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    ProfileKeyboard.get_change_profile_info_button()
                ],
                [
                    ProfileKeyboard.get_back_to_profile_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_profile_menu_keyboard():
        from app.bot.keyboards.main_manu import MainMenuKeyboard
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Личные данные', callback_data='me_menu'),
                ],
                [
                    InlineKeyboardButton(text='Аватар пользователя', callback_data='avatar_menu'),
                ],
                [
                    InlineKeyboardButton(text='Мои кэш-боксы', callback_data='cashbox_menu'),
                ],
                [
                    MainMenuKeyboard.back_to_main_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_back_profile_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    ProfileKeyboard.get_back_to_profile_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_empty_user_cashbox_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    ProfileKeyboard.get_create_user_cashbox_button()
                ],
                [
                    ProfileKeyboard.get_back_to_profile_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_user_cashbox_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    ProfileKeyboard.get_previous_user_cashbox_button(),
                    ProfileKeyboard.get_more_action_user_cashbox_button(),
                    ProfileKeyboard.get_next_user_cashbox_button()
                ],
                [
                    ProfileKeyboard.get_create_user_cashbox_button()
                ],
                [
                    ProfileKeyboard.get_back_to_profile_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_more_action_user_cashbox_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    ProfileKeyboard.get_change_user_cashbox_button(),
                    ProfileKeyboard.get_delete_user_cashbox_button()
                ],
                [
                    ProfileKeyboard.get_back_to_user_cashbox_button()
                ]
            ]
        )

    @staticmethod
    def get_provider_cashbox_menu_keyboard(provider_name):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    ProfileKeyboard.get_previous_provider_cashbox_button(),
                    ProfileKeyboard.get_provider_cashbox_button(provider_name),
                    ProfileKeyboard.get_next_provider_cashbox_button()
                ],
                [
                    ProfileKeyboard.get_back_to_profile_menu_from_providers_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_cashboxes_by_provider_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    ProfileKeyboard.get_previous_cashbox_by_provider_button(),
                    ProfileKeyboard.get_take_cashbox_by_provider_button(),
                    ProfileKeyboard.get_next_cashbox_by_provider_button()
                ],
                [
                    ProfileKeyboard.get_back_to_cashbox_provider_menu_button()
                ]
            ]
        )