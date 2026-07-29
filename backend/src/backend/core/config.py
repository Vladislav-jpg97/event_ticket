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
    redis_url: str
    app_name: str = "RecipeFinderAPI"
    secret_key: str | None = None
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    algorithm: str = "HS256"


settings = Settings()
