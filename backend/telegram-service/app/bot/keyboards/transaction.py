from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class TransactionKeyboard:

    @staticmethod
    def get_transaction_menu_button():
        return InlineKeyboardButton(text='💸 Транзакции', callback_data='transaction_menu')

    @staticmethod
    def get_back_transaction_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    TransactionKeyboard.get_back_to_select_subcategory_button()
                ]
            ]
        )

    @staticmethod
    def get_back_transaction_menu_button():
        return InlineKeyboardButton(text='Вернуться в меню транзакций', callback_data='transaction_menu')

    @staticmethod
    def get_make_transaction_menu_button():
        return InlineKeyboardButton(text='Записать новую транзакцию', callback_data='new_transaction_menu')

    @staticmethod
    def get_transaction_history_menu_button():
        return InlineKeyboardButton(text='Посмотреть историю записанных транзакций', callback_data='transaction_history_menu')

    @staticmethod
    def get_transaction_statistic_menu_button():
        return InlineKeyboardButton(text='Посмотреть статистику записанных транзакций', callback_data='transaction_statistic_menu')

    @staticmethod
    def get_transaction_menu_keyboard():
        from app.bot.keyboards.main_manu import MainMenuKeyboard
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    TransactionKeyboard.get_make_transaction_menu_button()
                ],
                [
                    TransactionKeyboard.get_transaction_statistic_menu_button()
                ],
                [
                    TransactionKeyboard.get_transaction_history_menu_button()
                ],
                [
                    MainMenuKeyboard.back_to_main_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_income_menu_button():
        return InlineKeyboardButton(text='Доходы', callback_data='transaction_type_income')

    @staticmethod
    def get_expense_menu_button():
        return InlineKeyboardButton(text='Расходы', callback_data='transaction_type_expense')

    @staticmethod
    def get_select_transaction_type_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    TransactionKeyboard.get_income_menu_button(),
                    TransactionKeyboard.get_expense_menu_button()
                ],
                [
                    TransactionKeyboard.get_back_transaction_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_empty_user_cashbox_menu_keyboard():
        from app.bot.keyboards.profile import ProfileKeyboard
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    ProfileKeyboard.get_create_user_cashbox_button()
                ],
                [
                    TransactionKeyboard.get_back_transaction_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_empty_category_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    TransactionKeyboard.get_back_transaction_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_select_user_cashbox_button():
        return InlineKeyboardButton(text='Выбрать', callback_data='select_user_cashbox_for_transaction')

    @staticmethod
    def get_previous_user_cashbox_button():
        return InlineKeyboardButton(text='◀️ Предыдущий', callback_data="transaction_user_cashbox_prev")

    @staticmethod
    def get_next_user_cashbox_button():
        return InlineKeyboardButton(text='Следующий ▶️', callback_data="transaction_user_cashbox_next")


    @staticmethod
    def get_user_cashbox_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    TransactionKeyboard.get_previous_user_cashbox_button(),
                    TransactionKeyboard.get_select_user_cashbox_button(),
                    TransactionKeyboard.get_next_user_cashbox_button()
                ],
                [
                    TransactionKeyboard.get_back_transaction_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_category_button(text, id):
        return InlineKeyboardButton(text=text, callback_data=f"select_category_{id}")

    @staticmethod
    def get_subcategory_button(text, id):
        return InlineKeyboardButton(text=text, callback_data=f"select_subcategory_{id}")

    @staticmethod
    def get_empty_category_button():
        return InlineKeyboardButton(text='', callback_data="noop")

    @staticmethod
    def get_next_category_button():
        return InlineKeyboardButton(text='Далее ➡️', callback_data='select_category_next')

    @staticmethod
    def get_next_subcategory_button():
        return InlineKeyboardButton(text='Далее ➡️', callback_data='select_subcategory_next')

    @staticmethod
    def get_previous_category_button():
        return InlineKeyboardButton(text='⬅️ Назад', callback_data='select_category_prev')

    @staticmethod
    def get_previous_subcategory_button():
        return InlineKeyboardButton(text='⬅️ Назад', callback_data='select_subcategory_prev')

    @staticmethod
    def get_count_category_page_button(page, total_pages):
        return InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop")

    @staticmethod
    def get_category_menu_subkeyboard(page, total_pages):
        return [
            TransactionKeyboard.get_previous_category_button(),
            TransactionKeyboard.get_count_category_page_button(page, total_pages),
            TransactionKeyboard.get_next_category_button()
        ]

    @staticmethod
    def get_subcategory_menu_subkeyboard(page, total_pages):
        return [
            TransactionKeyboard.get_previous_subcategory_button(),
            TransactionKeyboard.get_count_category_page_button(page, total_pages),
            TransactionKeyboard.get_next_subcategory_button()
        ]

    @staticmethod
    def get_category_menu_keyboard(buttons):
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_subcategory_menu_keyboard(buttons):
        return InlineKeyboardMarkup(inline_keyboard=buttons)


    @staticmethod
    def get_transaction_amount_button():
        return InlineKeyboardButton(text='Сумма транзакции', callback_data='get_transaction_amount')

    @staticmethod
    def get_transaction_comment_button():
        return InlineKeyboardButton(text='Комментарий', callback_data='get_transaction_comment')

    @staticmethod
    def get_transaction_location_button():
        return InlineKeyboardButton(text='Локация', callback_data='get_transaction_location')

    @staticmethod
    def get_transaction_vendor_button():
        return InlineKeyboardButton(text='Адресат транзакции', callback_data='get_transaction_vendor')

    @staticmethod
    def get_transaction_datetime_button():
        return InlineKeyboardButton(text='Дата и время', callback_data='get_transaction_datetime')

    @staticmethod
    def get_transaction_source_button():
        return InlineKeyboardButton(text='Источник транзакции', callback_data='get_transaction_source')

    @staticmethod
    def get_back_to_select_subcategory_button():
        return InlineKeyboardButton(text='Назад', callback_data='get_back_to_select')

    @staticmethod
    def get_create_new_income_button():
        return InlineKeyboardButton(text='Создать новую запись', callback_data='get_create_new_income')

    @staticmethod
    def get_create_new_expense_button():
        return InlineKeyboardButton(text='Создать новую запись', callback_data='get_create_new_expense')

    @staticmethod
    def get_new_income_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    TransactionKeyboard.get_transaction_amount_button(),
                    TransactionKeyboard.get_transaction_comment_button()
                ],
                [
                    TransactionKeyboard.get_transaction_datetime_button(),
                    TransactionKeyboard.get_transaction_source_button()
                ]
            ]
        )

    @staticmethod
    def get_done_new_income_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    TransactionKeyboard.get_transaction_amount_button(),
                    TransactionKeyboard.get_transaction_comment_button()
                ],
                [
                    TransactionKeyboard.get_transaction_datetime_button(),
                    TransactionKeyboard.get_transaction_source_button()
                ],
                [
                    TransactionKeyboard.get_create_new_income_button()
                ]
            ]
        )

    @staticmethod
    def get_new_expense_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    TransactionKeyboard.get_transaction_amount_button(),
                    TransactionKeyboard.get_transaction_comment_button()
                ],
                [
                    TransactionKeyboard.get_transaction_datetime_button(),
                ],
                [
                    TransactionKeyboard.get_transaction_location_button(),
                    TransactionKeyboard.get_transaction_vendor_button()
                ]
            ]
        )

    @staticmethod
    def get_new_done_expense_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    TransactionKeyboard.get_transaction_amount_button(),
                    TransactionKeyboard.get_transaction_comment_button()
                ],
                [
                    TransactionKeyboard.get_transaction_datetime_button(),
                ],
                [
                    TransactionKeyboard.get_transaction_location_button(),
                    TransactionKeyboard.get_transaction_vendor_button()
                ],
                [
                    TransactionKeyboard.get_create_new_expense_button()
                ]
            ]
        )

    @staticmethod
    def get_more_history_info_button():
        return InlineKeyboardButton(text='Посмотреть подробную историю\nмоих транзакция', callback_data='get_more_history_information')

    @staticmethod
    def def_get_history_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    TransactionKeyboard.get_more_history_info_button()
                ],
                [
                    TransactionKeyboard.get_back_transaction_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_more_statistic_info_button():
        return InlineKeyboardButton(text='Подробнее', callback_data='get_more_statistic_information')

    @staticmethod
    def get_statistic_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    TransactionKeyboard.get_more_statistic_info_button()
                ],
                [
                    TransactionKeyboard.get_back_transaction_menu_button()
                ]
            ]
        )





