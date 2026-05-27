import logging

from structs import NOT_CONNECTED, Message, MessageChain
from repositories import MessageChainRepo, UserRepo

logger = logging.getLogger(__name__.upper())


class ChatService:

    user_repo: UserRepo
    chain_repo: MessageChainRepo

    def __init__(self, user_repo: UserRepo, chain_repo: MessageChainRepo):
        self.user_repo = user_repo
        self.chain_repo = chain_repo

    def connect(self, user_id: int, chain_id: int) -> bool:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            logger.error("Cannot connect: user %s not found", user_id)
            return False

        old_chain_id = user.active_chain
        if old_chain_id != NOT_CONNECTED and old_chain_id != chain_id:
            self.chain_repo.safe_update(old_chain_id,
                                        lambda c: c.set_user(NOT_CONNECTED))
            logger.debug("Chain %s released from user %s", old_chain_id, user_id)

        if chain_id != NOT_CONNECTED:
            if not self.chain_repo.find_by_id(chain_id):
                logger.error("Connect failed: chain %s not found", chain_id)
                return False

            self.chain_repo.safe_update(chain_id,
                                        lambda c: c.set_user(user_id))
            logger.info("Message chain %s linked to user %s", chain_id,
                        user_id)

        success = self.user_repo.safe_update(
            user_id, lambda u: u.set_activity(chain_id))

        if success:
            action = "connected to chain %s" % chain_id if chain_id != NOT_CONNECTED else "disconnected"
            logger.info("User %s %s", user_id, action)

        return success

    def add_message_to_current_chain(self, user_id: int,
                                     message: Message) -> bool:
        user = self.user_repo.find_by_id(user_id)
        if not user or user.active_chain == NOT_CONNECTED:
            logger.error("User %s has no active chain", user_id)
            return False

        return self.chain_repo.update_messages(user.active_chain, (message, ))

    def create_chain_for_user(self, chain_id: int, user_id: int,
                              first_message: Message) -> bool:
        new_chain = MessageChain(chain_id,
                                 user_id,
                                 last_update_id=first_message.update_id,
                                 messages=(first_message, ))

        if not self.chain_repo.create(new_chain):
            logger.error("Failed to create chain %s", chain_id)
            return False

        return self.connect(user_id, chain_id)
