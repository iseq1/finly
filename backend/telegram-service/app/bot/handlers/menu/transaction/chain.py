from app.bot.handlers.menu.transaction.steps import GetSelectTransactionTypeHandler, GetUserCashboxInfoHandler, \
    CheckUserCashboxesHandler, ShowUserCashboxHandler, RememberUserCashboxHandler, GetCategoryInfoHandler, \
    CheckCategoryHandler, ShowCategoriesHandler, RememberCategoryHandler, GetSubcategoryByCategoryInfoHandler, \
    CheckSubcategoryHandler, ShowSubcategoriesHandler, RememberSubcategoryHandler, TakingTransactionInfoHandler, \
    WaitTransactionFieldHandler, TakingTransactionFieldHandler, CheckTransactionInfoHandler, MakeTransactionDataHandler, \
    SaveNewTransactionHandler, NotifySuccessesTransactionHandler, GetUserLatestTransactionInfoHandler, \
    ShowUserLatestTransactionInfoHandler, CheckUserLatestTransactionsInfoHandler, GetUserTransactionStatisticHandler, \
    CheckUserTransactionStatisticHandler, ShowUserTransactionStatisticHandler


class TransactionMenuChain:

    def get_handler_by_step(self, step: int, chain_func):
        current = chain_func()
        for _ in range(step):
            if current.next_handler is None:
                return None
            current = current.next_handler
        return current

    @staticmethod
    def get_transaction_chain():
        return GetSelectTransactionTypeHandler()

    @staticmethod
    def get_transaction_field_info_chain():
        return WaitTransactionFieldHandler(
            TakingTransactionFieldHandler(
                TakingTransactionInfoHandler(

                )
            )
        )

    @staticmethod
    def get_watch_history_transaction_chain():
        return GetUserLatestTransactionInfoHandler(
            CheckUserLatestTransactionsInfoHandler(
                ShowUserLatestTransactionInfoHandler()
            )
        )

    @staticmethod
    def get_watch_statistic_transaction_chain():
        return GetUserTransactionStatisticHandler(
            CheckUserTransactionStatisticHandler(
                ShowUserTransactionStatisticHandler(

                )
            )
        )

    @staticmethod
    def get_create_transaction_chain():
        return GetUserCashboxInfoHandler(
            CheckUserCashboxesHandler(
                ShowUserCashboxHandler(
                    RememberUserCashboxHandler(
                        GetCategoryInfoHandler(
                            CheckCategoryHandler(
                                ShowCategoriesHandler(
                                    RememberCategoryHandler(
                                        GetSubcategoryByCategoryInfoHandler(
                                            CheckSubcategoryHandler(
                                                ShowSubcategoriesHandler(
                                                    RememberSubcategoryHandler(
                                                        TakingTransactionInfoHandler(
                                                            CheckTransactionInfoHandler(
                                                                MakeTransactionDataHandler(
                                                                    SaveNewTransactionHandler(
                                                                        NotifySuccessesTransactionHandler(

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
                                )
                            )
                        )
                    )
                )
            )
        )