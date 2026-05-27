from typing import Tuple, NamedTuple, Sequence, Mapping
from dataclasses import dataclass, replace, field

NOT_CONNECTED = 0


class Message(NamedTuple):
    text: str
    is_bot: bool
    timestamp: float
    update_id: int


@dataclass(frozen=True, slots=True)
class MessageChain:
    id: int
    user_id: int
    last_update_id: int
    # Sequence
    messages: Tuple[Message, ...] = field(default_factory=tuple)

    def set_id(self, new_id: int) -> MessageChain:
        return replace(self, id=new_id)
    
    def set_user(self, user_id: int) -> MessageChain:
        return replace(self, user_id=user_id)
    
    def change_last_update_id(self, new_id: int) -> MessageChain:
        return replace(self, last_update_id=new_id)

    def put_messages(self, new_messages: Tuple[Message, ...]) -> MessageChain:
        combined = self.messages + new_messages
        new_update_id = combined[-1].update_id if combined else self.last_update_id
        return replace(self, messages=combined, last_update_id=new_update_id)


@dataclass(frozen=True, slots=True)
class UserData:
    id: int
    # Mapping
    data: dict = field(default_factory={})
    active_chain: int = field(default=NOT_CONNECTED)

    def put_data(self, new_data: dict) -> UserData:
        return replace(self, data=new_data.copy())

    def set_id(self, new_id: int) -> UserData:
        return replace(self, id=new_id)

    def set_activity(self, chain_id: int = NOT_CONNECTED) -> UserData:
        return replace(self, active_chain=chain_id)
