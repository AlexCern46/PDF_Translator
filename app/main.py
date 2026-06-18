from fastapi import FastAPI

from app.api.endpoints import router
from app.core.minio_config import check_bucket_exists

app = FastAPI()


app.include_router(router)


@app.on_event('startup')
def startup_event():
    check_bucket_exists()
