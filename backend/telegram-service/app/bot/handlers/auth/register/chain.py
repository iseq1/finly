from app.bot.handlers.auth.register.steps import TelegramRegisterHandler, FSMUpdateHandler, SendWelcomeHandler


class RegisterChain:

    @staticmethod
    def get_register_chain():
        return TelegramRegisterHandler(
            FSMUpdateHandler(
                SendWelcomeHandler()
            )
        )