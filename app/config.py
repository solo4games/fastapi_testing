from typing import Literal

from pydantic import model_validator, Field, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]

    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_HOST: str
    DATABASE_URL: str = Field(default="")

    BROKER_URL: str

    @model_validator(mode="after")
    def get_database_url(cls, values):
        values.DATABASE_URL = (
            f"postgresql+asyncpg://{values.DB_USER}:{values.DB_PASSWORD}@{values.DB_HOST}:{values.DB_PORT}/{values.DB_DATABASE}"
        )
        return values

    TEST_DB_PORT: str
    TEST_DB_USER: str
    TEST_DB_PASSWORD: str
    TEST_DB_DATABASE: str
    TEST_DB_HOST: str
    TEST_DATABASE_URL: str = Field(default="")

    @model_validator(mode="after")
    def get_test_database_url(cls, values):
        values.TEST_DATABASE_URL = (
            f"postgresql+asyncpg://{values.TEST_DB_USER}:{values.TEST_DB_PASSWORD}@{values.TEST_DB_HOST}:{values.TEST_DB_PORT}/{values.TEST_DB_DATABASE}"
        )
        return values

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

settings = Settings()