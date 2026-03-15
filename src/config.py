import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mlb_api_base_url: str = 'https://statsapi.mlb.com/api/v1'
    mlb_api_schedule_endpoint: str = '/schedule?sportId=1'
    mlb_api_standings_endpoint: str = '/standings?leagueId=103,104'
    mlb_api_hitting_stats_endpoint: str = '/stats?stats=season&group=hitting&playerPool=all&season=2023'
    mlb_api_pitching_stats_endpoint: str = '/stats?stats=season&group=pitching&playerPool=all&season=2023'
    output_dir: str = './data'
    log_level: str = 'INFO'
    retries: int = 3
    retry_delay_seconds: int = 5

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'

settings = Settings()
