from abc import ABC, abstractmethod


class BaseFileProcessor(ABC):
    @abstractmethod
    def read(self, file: bytes) -> object:
        ...

    @abstractmethod
    def process(self, file_data: object) -> str:
        ...
