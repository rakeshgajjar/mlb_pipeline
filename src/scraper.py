import json
import logging
import os
from datetime import datetime
import requests
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from src.config import settings

logger = logging.getLogger(__name__)

class MLBScraper:
    def __init__(self):
        self.base_url = settings.mlb_api_base_url
        self.endpoints = {
            "schedule": settings.mlb_api_schedule_endpoint,
            "standings": settings.mlb_api_standings_endpoint,
            "hitting_stats": settings.mlb_api_hitting_stats_endpoint,
            "pitching_stats": settings.mlb_api_pitching_stats_endpoint
        }
        self.output_dir = settings.output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.session = requests.Session()

    @retry(
        stop=stop_after_attempt(settings.retries),
        wait=wait_fixed(settings.retry_delay_seconds),
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout)),
        reraise=True
    )
    def fetch_data(self, endpoint: str) -> dict:
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Fetching data from {url}")
        
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Successfully fetched data from {endpoint}")
        return data

    def save_json(self, data: dict, name: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mlb_{name}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        logger.info(f"Saved raw JSON {name} to {filepath}")
        return filepath

    def run(self) -> dict:
        filepaths = {}
        for name, endpoint in self.endpoints.items():
            try:
                data = self.fetch_data(endpoint)
                filepath = self.save_json(data, name)
                filepaths[name] = filepath
            except Exception as e:
                logger.error(f"Scraper failed for {name}: {e}")
                # We can choose to raise or continue
                # We will continue to try and fetch others
        return filepaths
