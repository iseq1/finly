from app.bot.handlers.menu.profile.steps import EditProfileInfoHandler, TakingNewFieldHandler, WaitNewFieldHandler, GetChangeProfileHandler, GetProfileInfoHandler, SendProfileInfoHandler, GetUserCashboxesHandler, GetUserBudgetHandler, GetUserTransactionsHandler, GenerateProfileMessageHandler


class ProfileMenuChain:

    def get_handler_by_step(self, step: int):
        chain = self.get_profile_chain()
        current = chain
        for _ in range(step):
            if current.next_handler is None:
                return None
            current = current.next_handler
        return current

    @staticmethod
    def get_change_profile_info_menu_chain():
        return GetChangeProfileHandler()

    @staticmethod
    def get_profile_chain():
        return GetProfileInfoHandler(
            GetUserCashboxesHandler(
                GetUserTransactionsHandler(
                    GetUserBudgetHandler(
                        GenerateProfileMessageHandler(
                            SendProfileInfoHandler(
                                GetChangeProfileHandler(
                                    WaitNewFieldHandler(
                                        TakingNewFieldHandler(
                                            EditProfileInfoHandler(

                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )