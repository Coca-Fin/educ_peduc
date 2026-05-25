from logging import Logger

from structs import NOT_CONNECTED, Message
from repositories import MessageChainRepo, UserRepo


class ChatService:

    def __init__(self, user_repo: UserRepo, chain_repo: MessageChainRepo,
                 logger: Logger):
        self.user_repo = user_repo
        self.chain_repo = chain_repo
        self._logger = logger

    def connect(self, user_id: int, chain_id: int) -> bool:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            self._logger.error(f"Cannot connect: user {user_id} not found")
            return False

        old_chain_id = user.active_chain
        if old_chain_id != NOT_CONNECTED and old_chain_id != chain_id:
            self.chain_repo.safe_update(old_chain_id,
                                        lambda c: c.set_activity(False))
            self._logger.debug(f"Old chain {old_chain_id} deactivated")

        connect = chain_id != NOT_CONNECTED
        if connect:
            chain = self.chain_repo.find_by_id(chain_id)
            if not chain:
                self._logger.error(f"Chain {chain_id} not found")
                return False
            self.chain_repo.safe_update(chain_id,
                                        lambda c: c.set_activity(True))

        self.user_repo.safe_update(user_id, lambda u: u.set_activity(chain_id))

        action = "connected to chain" if connect else "disconnected"
        self._logger.info(f"User {user_id} {action} {chain_id}")
        return True

    def add_message_to_current_chain(self, user_id: int,
                                     message: Message) -> bool:
        user = self.user_repo.find_by_id(user_id)
        if not user or user.active_chain == NOT_CONNECTED:
            self._logger.error(f"User {user_id} has no active chain")
            return False

        return self.chain_repo.update_messages(user.active_chain, (message, ))
