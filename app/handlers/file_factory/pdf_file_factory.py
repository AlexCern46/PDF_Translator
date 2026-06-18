from app.handlers.file_factory.base_file_factory import BaseFileFactory
from app.handlers.file_uploader.base_file_processor import BaseFileProcessor
from app.handlers.file_uploader.pdf_file_processor import PdfFileProcessor


class PdfFileFactory(BaseFileFactory):
    def create_file(self) -> BaseFileProcessor:
        return PdfFileProcessor()
