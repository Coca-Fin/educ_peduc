from typing import List, Protocol


class Identifiable(Protocol):
    id: int


class MemoryProtocol[T](Protocol):

    """
        Если будет необходимо, то этот интерфейс нужно поделить на read/write.
        Для обеспечения многопоточного доступа.

        Не забываем, что Python хочет сочетать и EAFP и LBYL
    """

    def get(self, key: int) -> T | None:
        ...

    def put(self, key: int, value: T) -> None:
        ...

    def pop(self, key: int) -> T | None:
        ...

    def clear(self) -> None:
        ...

    def __contains__(self, key: int) -> bool:
        ...

    def __getitem__(self, key: int) -> T:
        ...

    def __setitem__(self, key: int, value: T) -> None:
        ...


class RepoProtocol[T](Protocol):

    def find_by_id(self, id: int) -> T | None:
        ...

    def create(self, id: int, **kwargs) -> T | None:
        ...

    def all(self) -> List[T]:
        ...

    def update(self, id: int, obj: T) -> None:
        ...

    def delete(self, id: int) -> T | None:
        ...

    def clear(self) -> None:
        ...