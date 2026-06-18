import tempfile

from deep_translator import GoogleTranslator

from app.core.celery_config import celery
from app.core.minio_config import minio_client, BUCKET_FOR_DOWNLOADS


@celery.task
def translate(text: str, language: str) -> str:
    return GoogleTranslator(source='en', target=language).translate(text)


@celery.task
def save_translated_texts(texts: list[str]) -> None:
    with tempfile.NamedTemporaryFile(mode='w') as temp_file:
        for text in texts:
            temp_file.write(text + '\n')

        minio_client.fput_object(BUCKET_FOR_DOWNLOADS, f'{save_translated_texts.request.id}.txt', temp_file.name)
