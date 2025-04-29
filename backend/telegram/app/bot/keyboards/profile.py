from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class ProfileKeyboard:

    @staticmethod
    def get_profile_menu_button():
        return InlineKeyboardButton(text='Профиль', callback_data='profile_menu')

    @staticmethod
    def get_change_profile_info_button():
        return InlineKeyboardButton(text='Обновить данные', callback_data='change_profile_info_menu')

    @staticmethod
    def back_to_profile_menu_button():
        return InlineKeyboardButton(text='Вернуться в меню профиля', callback_data='profile_menu')

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
                    ProfileKeyboard.back_to_profile_menu_button()
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
                    ProfileKeyboard.back_to_profile_menu_button()
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
                    ProfileKeyboard.back_to_profile_menu_button()
                ]
            ]
        )