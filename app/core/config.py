from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
