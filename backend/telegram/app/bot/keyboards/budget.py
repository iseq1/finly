from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class BudgetKeyboard:

    @staticmethod
    def get_budget_menu_button():
        return InlineKeyboardButton(text='Бюджеты', callback_data='budget_menu')

    @staticmethod
    def get_back_to_budget_menu_button():
        return InlineKeyboardButton(text='Вернуться в меню бюджетов', callback_data='budget_menu')

    @staticmethod
    def get_back_budget_menu_button():
        return InlineKeyboardButton(text='Вернуться в меню бюджетов', callback_data='budget_menu')

    @staticmethod
    def get_back_budget_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    BudgetKeyboard.get_back_budget_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_my_budgets_button():
        return InlineKeyboardButton(text='Мои бюджеты', callback_data='get_my_budget_menu')

    @staticmethod
    def get_create_new_budget_button():
        return InlineKeyboardButton(text='Создать новый бюджет', callback_data='create_new_budget')

    @staticmethod
    def get_balance_snapshot_button():
        return InlineKeyboardButton(text='Состояние баланса', callback_data='get_my_balance_snapshot_menu')

    @staticmethod
    def get_budget_menu_keyboard():
        from app.bot.keyboards.main_manu import MainMenuKeyboard
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    BudgetKeyboard.get_my_budgets_button()
                ],
                [
                    BudgetKeyboard.get_create_new_budget_button()
                ],
                [
                    BudgetKeyboard.get_balance_snapshot_button()
                ],
                [
                    MainMenuKeyboard.back_to_main_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_empty_budgets_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    BudgetKeyboard.get_create_new_budget_button()
                ],
                [
                    BudgetKeyboard.get_back_to_budget_menu_button()
                ]
            ]
        )

    @staticmethod
    def get_select_user_budget_button():
        return InlineKeyboardButton(text='Выбрать', callback_data='select_user_budget')

    @staticmethod
    def get_previous_user_budget_button():
        return InlineKeyboardButton(text='◀️ Предыдущий', callback_data="user_budget_prev")

    @staticmethod
    def get_next_user_budget_button():
        return InlineKeyboardButton(text='Следующий ▶️', callback_data="user_budget_ext")

    @staticmethod
    def get_user_budgets_menu_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    BudgetKeyboard.get_previous_user_budget_button(),
                    BudgetKeyboard.get_select_user_budget_button(),
                    BudgetKeyboard.get_next_user_budget_button()
                ],
                [
                    BudgetKeyboard.get_back_to_budget_menu_button()
                ]
            ]
        )




