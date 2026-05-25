from typing import Callable, List, Tuple
from logging import Logger

from protocols import MemoryProtocol
from structs import NOT_CONNECTED, Message, MessageChain, UserData


class BaseRepo[T]:

    _logger: Logger
    _container: MemoryProtocol[T]
    _entity_name: str

    def __init__(self, logger: Logger, container: MemoryProtocol[T], entity_name: str) -> None:
        self._logger = logger
        self._container = container
        self._name = entity_name

    def find_by_id(self, entity_id: int) -> T | None:
        return self._container.get(entity_id)

    def delete(self, entity_id: int) -> T | None:
        item = self._container.pop(entity_id)
        if item:
            self._logger.debug(f"{self._name} {entity_id} deleted")
        return item

    def clear(self) -> None:
        self._container.clear()
        self._logger.debug(f"{self._name} container cleared")

    def safe_create(self, entity_id: int, factory: Callable[[], T]) -> T | None:
        if entity_id in self._container:
            self._logger.debug(f"{self._name} {entity_id} already exists")
            return None
        
        entity = factory()
        # self._container.put(entity_id, entity)
        self._container[entity_id] = entity
        self._logger.debug(f"{self._name} {entity_id} created")
        return entity

    def safe_update(self, entity_id: int, factory: Callable[[T], T]) -> bool:
        entity = self.find_by_id(entity_id)
        if entity is None:
            self._logger.debug(f"{self._name} {entity_id} doesn't exist")
            return False
        
        updated_entity = factory(entity)
        # self._container.put(entity_id, updated_entity)
        self._container[entity_id] = updated_entity
        self._logger.debug(f"{self._name} {entity_id} updated with {factory.__qualname__}")
        return True
    
    def safe_move(self, old_id: int, new_id: int, factory: Callable[[T, int], T]) -> bool:
        if old_id == new_id:
            return True
        
        if new_id in self._container:
            self._logger.debug(f"{self._name} {new_id} is already taken")
            return False
        
        entity = self._container.pop(old_id)
        if entity is None:
            self._logger.debug(f"{self._name} {old_id} doesn't exist")
            return False
        
        # self._container.put(new_id, factory(new_id))
        self._container[new_id] = factory(new_id)
        self._logger.debug(f"{self._name} {old_id} moved to {new_id}")
        return True
    

class UserRepo(BaseRepo[UserData]):
    
    def create(self, user_id: int, data: dict = None) -> UserData | None:
        return self.safe_create(
            user_id, 
            lambda: UserData(user_id, (data or {}).copy(), NOT_CONNECTED)
        )
    
    def all(self) -> List[UserData]:
        # Кривая реализцаия факт, но ноооо
        return list(self._container.values())

    def update(self, user_id: int, obj: UserData) -> None:
        if user_id != obj.id:
            user = self._container.pop(user_id)
            if user:
                # self._container.put(obj.id, user.update_id(obj.id))
                self._container[obj.id] = user.set_id(obj.id)
                self._logger.debug(f"User {user_id} moved to {obj.id}")

        success = self.safe_update(obj.id, lambda u: u.put_data(obj.data))
        
        if success:
            self._logger.debug(f"User {obj.id} updated with {obj}")

    def update_data(self, user_id: int, new_data: dict) -> bool:
        return self.safe_update(user_id, lambda u: u.put_data(new_data))
    
    def update_id(self, old_id: int, new_id: int) -> bool:
        return self.safe_move(old_id, new_id, lambda u: u.set_id(new_id))
    
    
class MessageChainRepo(BaseRepo[MessageChain]):

    def create(self, chain_id: int, message: Message) -> MessageChain | None:
        return self.safe_create(
            chain_id, 
            lambda: MessageChain(chain_id, (message,), False)
        )
    
    def all(self) -> List[MessageChain]:
        # Кривая реализцаия факт, но ноооо
        return list(self._container.values())
    
    def update(self, chain_id: int, obj: MessageChain) -> None:
        self.update_messages(chain_id, obj.messages)
        self._logger.debug(f"Chain {chain_id} updated")

    def update_messages(self, chain_id: int, new_messages: Tuple[Message, ...]) -> bool:
        return self.safe_update(
            chain_id, 
            lambda c: c.add_messages(new_messages)
        )
    
    def update_id(self, old_id: int, new_id: int) -> bool:
        return self.safe_move(old_id, new_id, lambda c: c.set_id(new_id))