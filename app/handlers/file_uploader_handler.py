from celery import chain, group
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
from fastapi import HTTPException

from app.handlers.file_factory.pdf_file_factory import PdfFileFactory
from app.services.celery_service import translate, save_translated_texts


class FileUploaderHandler:
    def __init__(self):
        self.file_factories = {
            'pdf': PdfFileFactory(),
        }

    def handle(self, file: bytes, filename: str, language: str):
        file_type = self.determine_file_type(filename)

        if file_type not in self.file_factories:
            raise HTTPException(status_code=500, detail=f"Unsupported file type: {file_type}")

        file_factory = self.file_factories[file_type]
        file_uploader = file_factory.create_file(file)

        pdf_document = file_uploader.read()

        extraction_tasks = self.create_tasks(filename, language, pdf_document.page_count)
        return extraction_tasks().id

    @staticmethod
    def determine_file_type(filename: str) -> str:
        # TODO determining MIME file type
        if filename:
            return filename.split(".")[-1].lower()
        return 'unknown'

    @staticmethod
    def check_language_code(language: str = 'ru') -> str:
        if language not in GOOGLE_LANGUAGES_TO_CODES.values():
            raise HTTPException(status_code=500, detail='Invalid language code')
        return language

    @staticmethod
    def create_tasks(filename: str, language: str, num_of_pages: int):
        return chain(group(
            translate.s(f'{filename}/{page_num + 1}', language) for page_num in range(num_of_pages)),
            save_translated_texts.s())
