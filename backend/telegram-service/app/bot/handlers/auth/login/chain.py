from app.bot.handlers.auth.login.steps import TelegramLoginHandler, FSMUpdateHandler, SendWelcomeHandler


class LoginChain:

    @staticmethod
    def get_login_chain():
        return TelegramLoginHandler(
            FSMUpdateHandler(
                SendWelcomeHandler()
            )
        )