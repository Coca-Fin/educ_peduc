import logging
from typing import Callable, List, Tuple

from protocols import MemoryProtocol
from structs import Message, MessageChain, UserData

logger = logging.getLogger(__name__.upper())


class BaseRepo[T]:

    _container: MemoryProtocol[T]
    _name: str

    def __init__(self, entity_name: str) -> None:
        self._name = entity_name

        # Пока индекс только id, хватит и dict
        self._container = {}

    def create(self, entity: T) -> T | None:
        if not hasattr(entity, "id"):
            logger.exception("%s entity without id", self._name)
            raise AttributeError("entity %s doesn't have id", entity)

        if entity.id in self._container:
            logger.debug("%s %s already exists", self._name, entity.id)
            return None
        
        # self._container.put(entity_id, entity)
        self._container[entity.id] = entity
        logger.debug("%s %s created", self._name, entity.id)
        return entity

    def find_by_id(self, entity_id: int) -> T | None:
        return self._container.get(entity_id)
    
    def all(self) -> List[T]:
        # Кривая реализцаия факт, но ноооо
        return list(self._container.values())

    def delete(self, entity_id: int) -> T | None:
        item = self._container.pop(entity_id)
        if item:
            logger.debug("%s %s deleted", self._name, entity_id)
        return item

    def clear(self) -> None:
        self._container.clear()
        logger.debug("%s container cleared", self._name)

    # Гарантия lambda, что переданный аргумент в функцию будет существующей сущностью
    def safe_update(self, entity_id: int, factory: Callable[[T], T]) -> bool:
        entity = self.find_by_id(entity_id)
        if entity is None:
            logger.debug("%s %s doesn't exist", self._name, entity_id)
            return False
        
        updated_entity = factory(entity)
        # self._container.put(entity_id, updated_entity)
        self._container[entity_id] = updated_entity
        logger.debug("%s %s updated with %s", self._name, entity_id, factory.__qualname__)
        return True
    
    def safe_move(self, old_id: int, new_id: int, factory: Callable[[T, int], T]) -> bool:
        if old_id == new_id:
            return True
        
        if new_id in self._container:
            logger.debug("%s %s is already taken", self._name, new_id)
            return False
        
        entity = self._container.pop(old_id)
        if entity is None:
            logger.debug("%s %s doesn't exist", self._name, old_id)
            return False
        
        # self._container.put(new_id, factory(entity, new_id))
        self._container[new_id] = factory(entity, new_id)
        logger.debug("%s %s moved to %s", self._name, old_id, new_id)
        return True
    

class UserRepo(BaseRepo[UserData]):

    def __init__(self):
        super().__init__("user")

    def update_data(self, user_id: int, new_data: dict) -> bool:
        return self.safe_update(user_id, lambda u: u.put_data(new_data))
    
    def update_id(self, old_id: int, new_id: int) -> bool:
        return self.safe_move(old_id, new_id, lambda u, i: u.set_id(i))
    
    
class MessageChainRepo(BaseRepo[MessageChain]):

    def __init__(self):
        super().__init__("message_chain")

    def update_messages(self, chain_id: int, new_messages: Tuple[Message, ...]) -> bool:
        return self.safe_update(
            chain_id, 
            lambda c: c.put_messages(new_messages)
        )
    
    def update_id(self, old_id: int, new_id: int) -> bool:
        return self.safe_move(old_id, new_id, lambda c, i: c.set_id(i))