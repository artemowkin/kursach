from pathlib import Path

from pydantic import BaseSettings


BASE_DIR = Path(__file__).parent.parent


class ProjectSettings(BaseSettings):
    database_url: str

    class Config:
        env_file = BASE_DIR / '.env'


settings = ProjectSettings()
