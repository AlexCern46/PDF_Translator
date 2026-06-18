from fastapi import HTTPException
from minio import Minio
from minio.error import S3Error

from app.core.config import settings

minio_client = Minio(settings.MINIO_ENDPOINT,
                     access_key=settings.MINIO_ACCESS_KEY,
                     secret_key=settings.MINIO_SECRET_KEY,
                     secure=False)


BUCKET_FOR_UPLOADS = 'upload-files'
BUCKET_FOR_DOWNLOADS = 'download-files'


def check_bucket_exists():
    try:
        if not minio_client.bucket_exists(BUCKET_FOR_UPLOADS):
            minio_client.make_bucket(BUCKET_FOR_UPLOADS)

        if not minio_client.bucket_exists(BUCKET_FOR_DOWNLOADS):
            minio_client.make_bucket(BUCKET_FOR_DOWNLOADS)

    except S3Error as e:
        raise HTTPException(status_code=500, detail=f'MinIO error: {e}')
