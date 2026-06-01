import os
from datetime import datetime
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.
    
    Configuration can be overridden via .env file or environment variables.
    """
    
    mlb_api_base_url: str = 'https://statsapi.mlb.com/api/v1'
    mlb_api_schedule_endpoint: str = '/schedule?sportId=1'
    mlb_api_standings_endpoint: str = '/standings?leagueId=103,104'
    # Current season defaults to the current year
    current_season: int = Field(default_factory=lambda: datetime.now().year)
    mlb_api_hitting_stats_endpoint: str = Field(
        default_factory=lambda: f'/stats?stats=season&group=hitting&playerPool=all&season={datetime.now().year}'
    )
    mlb_api_pitching_stats_endpoint: str = Field(
        default_factory=lambda: f'/stats?stats=season&group=pitching&playerPool=all&season={datetime.now().year}'
    )
    output_dir: str = './data'
    log_level: str = 'INFO'
    retries: int = 3
    retry_delay_seconds: int = 5

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'


settings: Settings = Settings()
