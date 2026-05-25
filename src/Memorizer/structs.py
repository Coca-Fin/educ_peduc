from typing import Tuple, NamedTuple, Mapping
from dataclasses import dataclass, replace

NOT_CONNECTED = -1


class Message(NamedTuple):
    text: str
    is_bot: bool
    timestamp: float


@dataclass(frozen=True, slots=True)
class MessageChain:
    id: int
    messages: Tuple[Message, ...]
    is_active: bool

    def set_id(self, new_id: int) -> MessageChain:
        return replace(self, id=new_id)

    def set_activity(self, flag: bool) -> MessageChain:
        return replace(self, is_active=flag)

    def add_messages(self, new_messages: Tuple[Message, ...]) -> MessageChain:
        return replace(self, messages=self.messages + new_messages)


@dataclass(frozen=True, slots=True)
class UserData:
    id: int
    data: dict
    active_chain: int

    def put_data(self, new_data: dict) -> UserData:
        return replace(self, data=new_data.copy())

    def set_id(self, new_id: int) -> UserData:
        return replace(self, id=new_id)

    def set_activity(self, chain_id: int = NOT_CONNECTED) -> UserData:
        return replace(self, active_chain=chain_id)
