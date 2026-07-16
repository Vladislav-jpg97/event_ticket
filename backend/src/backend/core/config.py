from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
BASE_DIR = Path(__file__).resolve().parents[3]
env_path = BASE_DIR / '.env'

print(f"Ищу .env файл здесь: {env_path}")
print(f"Файл существует?: {env_path.exists()}")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding='utf-8',
        extra='ignore'
    )
    database_url: str

settings = Settings()