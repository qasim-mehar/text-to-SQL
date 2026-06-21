from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    MISTRAL_API_KEY: str
    MODEL_NAME: str = "mistral-medium-3-5"
    DEBUG: bool = False

    @property
    def db_path(self) -> Path:
        # Goes: core/ -> app/ -> backend/ -> project_root/
        return Path(__file__).resolve().parent.parent.parent.parent / "company.db"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.db_path}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
