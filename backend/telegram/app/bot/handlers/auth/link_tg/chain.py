from app.bot.handlers.auth.link_tg.steps import FirstStepTelegramLinkHandler, SecondStepTelegramLinkHandler, \
    TakingEmaiHandler, TakingPasswordHandler, TelegramLoginHandler, FSMUpdateHandler, SendWelcomeHandler, \
    MakeLinkHandler


class LinkTelegramChain:

    @staticmethod
    def get_link_chain():
        return FirstStepTelegramLinkHandler(
            TakingEmaiHandler(
                SecondStepTelegramLinkHandler(
                    TakingPasswordHandler(
                        TelegramLoginHandler(
                            FSMUpdateHandler(
                                MakeLinkHandler(
                                    SendWelcomeHandler()
                                )
                            )
                        )
                    )
                )
            )
        )

    def get_handler_by_step(self, step: int):
        chain = self.get_link_chain()
        current = chain
        for _ in range(step):
            if current.next_handler is None:
                return None
            current = current.next_handler
        return current