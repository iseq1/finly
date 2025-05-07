from app.bot.handlers.menu.budget.steps import GetUserBudgetInfoHandler, CheckUserBudgetsInfoHandler, \
    GetCategoryInfoForBudgetsHandler, GetSubcategoryInfoForBudgetsHandler, GetUserCashboxInfoForBudgetsHandler, \
    CheckUserBudgetsAdditionalInfoHandler, ShowUserBudgetsHandler, CheckChosenBudgetHandler, GetDetailBudgetInfoHandler, \
    ShowDetailBudgetInfoHandler


class BudgetMenuChain:

    def get_handler_by_step(self, step: int, chain_func):
        current = chain_func()
        for _ in range(step):
            if current.next_handler is None:
                return None
            current = current.next_handler
        return current

    def get_user_budgets_chain(self):
        return GetUserBudgetInfoHandler(
            CheckUserBudgetsInfoHandler(
                GetCategoryInfoForBudgetsHandler(
                    GetSubcategoryInfoForBudgetsHandler(
                        GetUserCashboxInfoForBudgetsHandler(
                            CheckUserBudgetsAdditionalInfoHandler(
                                ShowUserBudgetsHandler(
                                    CheckChosenBudgetHandler(
                                        GetDetailBudgetInfoHandler(
                                            ShowDetailBudgetInfoHandler(

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