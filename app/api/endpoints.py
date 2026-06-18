from datetime import timedelta
from http import HTTPStatus

from celery.result import AsyncResult
from fastapi import APIRouter, UploadFile, Depends, File
from fastapi.responses import JSONResponse

from app.core.minio_config import minio_client, BUCKET_FOR_DOWNLOADS
from app.handlers.file_uploader_handler import FileUploaderHandler

router = APIRouter(prefix="/files")


@router.post('/upload/')
async def upload_pdf(language: str = Depends(FileUploaderHandler.check_language_code), file: UploadFile = File(...)):
    file_data = await file.read()
    extraction_tasks_id = FileUploaderHandler().handle(file_data, file.filename, language)
    return JSONResponse(content={'task_id': extraction_tasks_id})


@router.get('/task-status/{task_id}')
def get_task_status(task_id: str):
    async_result = AsyncResult(task_id)
    content, status_code = {'status': str(async_result.status)}, HTTPStatus.CONTINUE
    if async_result.successful():
        content['download_url'] = minio_client.presigned_get_object(BUCKET_FOR_DOWNLOADS, task_id, timedelta(days=1))
        status_code = HTTPStatus.OK
    return JSONResponse(content=content, status_code=status_code)
