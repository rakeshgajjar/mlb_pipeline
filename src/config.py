import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mlb_api_base_url: str = 'https://statsapi.mlb.com/api/v1'
    mlb_api_endpoint: str = '/schedule?sportId=1'
    output_dir: str = './data'
    log_level: str = 'INFO'
    retries: int = 3
    retry_delay_seconds: int = 5

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
