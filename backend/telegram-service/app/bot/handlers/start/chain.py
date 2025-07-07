from .steps import SendStartMessageHandler


class StartChain():

    @staticmethod
    def get_start_chain():
        return SendStartMessageHandler()
