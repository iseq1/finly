from app.bot.handlers.menu.steps import SendMainMenuMessageHandler, SendProfileHandler, SendTransactionHandler, \
    SendBudgetHandler


class MainMenuChain:

    @staticmethod
    def get_start_chain():
        return SendMainMenuMessageHandler()

    @staticmethod
    def get_profile_chain():
        return SendProfileHandler()

    @staticmethod
    def get_transaction_chain():
        return SendTransactionHandler()

    @staticmethod
    def get_budget_chain():
        return SendBudgetHandler()