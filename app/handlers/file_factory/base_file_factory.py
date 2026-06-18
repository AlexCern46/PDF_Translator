from abc import ABC, abstractmethod

from app.handlers.file_uploader.base_file_processor import BaseFileProcessor


class BaseFileFactory(ABC):
    @abstractmethod
    def create_file(self) -> BaseFileProcessor:
        ...
