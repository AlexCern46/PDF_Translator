import io
import tempfile
from io import BytesIO

import fitz
from PIL import Image
from fastapi.logger import logger
from fitz import Document
from minio.error import MinioException
from pytesseract import pytesseract

from app.core.celery_config import celery
from app.core.minio_config import minio_client, BUCKET_FOR_UPLOADS
from app.handlers.file_uploader.base_file_processor import BaseFileProcessor


class PdfFileProcessor(BaseFileProcessor):
    def read(self, file: bytes) -> object:
        pdf_document = fitz.open(stream=file)
        for page, page_num in self.split_on_pages(pdf_document):
            self.upload_page_to_object_storage(pdf_document.name, page, page_num)
        return pdf_document

    @celery.task
    def process(self, file_name: str) -> str:
        temp_file = tempfile.NamedTemporaryFile()
        minio_client.fget_object(BUCKET_FOR_UPLOADS, file_name, temp_file.name)

        page = pdf_document.load_page(0)
        pix = page.get_pixmap()
        with Image.open(BytesIO(pix.tobytes())) as img:
            text = pytesseract.image_to_string(img, lang='eng')
            text = text.replace('\n', ' ').replace('  ', '\n')
            text = f'----- {file_name.split("/")[-1]} page -----\n' + text
            return text

    @staticmethod
    def split_on_pages(file_data: object):
        pdf_document: Document = file_data
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            page = page.get_pixmap()
            yield page, page_num

    @staticmethod
    def upload_page_to_object_storage(filename: str, page, page_num: int) -> None:
        file_name = f'{filename}/{page_num + 1}'

        pdf_bytes = page.tobytes()
        pdf_buffer = io.BytesIO(pdf_bytes)

        try:
            minio_client.put_object(BUCKET_FOR_UPLOADS, file_name, pdf_buffer, len(pdf_bytes))
        except Exception:
            logger.error("")
            # remove this and use fastapi @app.exception_handler decorator
            raise MinioException()

