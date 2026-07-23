from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]
env_path = BASE_DIR / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding='utf-8',
        extra='ignore'
    )

    database_url: str
    debug: bool = False

    # Добавь остальные поля, которые планируешь использовать (с дефолтами или опциональные):
    app_name: str = "RecipeFinderAPI"
    secret_key: str | None = None
    # При необходимости добавь остальные поля из .env


settings = Settings()
