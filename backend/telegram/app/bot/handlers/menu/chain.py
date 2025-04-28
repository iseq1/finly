from app.bot.handlers.menu.steps import SendMainMenuMessageHandler, SendProfileHandler


class MainMenuChain:

    @staticmethod
    def get_start_chain():
        return SendMainMenuMessageHandler()

    @staticmethod
    def get_profile_chain():
        return SendProfileHandler()