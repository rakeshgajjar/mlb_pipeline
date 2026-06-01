import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from src.config import settings

logger: logging.Logger = logging.getLogger(__name__)


class MLBScraper:
    """Scrapes MLB data from statsapi.mlb.com and saves it as JSON files."""
    
    def __init__(self) -> None:
        """Initialize the MLB scraper with configured endpoints and session."""
        self.base_url: str = settings.mlb_api_base_url
        self.endpoints: Dict[str, str] = {
            "schedule": settings.mlb_api_schedule_endpoint,
            "standings": settings.mlb_api_standings_endpoint,
            "hitting_stats": settings.mlb_api_hitting_stats_endpoint,
            "pitching_stats": settings.mlb_api_pitching_stats_endpoint
        }
        self.output_dir: str = settings.output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.session: requests.Session = requests.Session()

    @retry(
        stop=stop_after_attempt(settings.retries),
        wait=wait_fixed(settings.retry_delay_seconds),
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout)),
        reraise=True
    )
    def fetch_data(self, endpoint: str) -> Dict:
        """Fetch JSON data from MLB API endpoint with retry logic.
        
        Args:
            endpoint: The API endpoint path (e.g., '/schedule?sportId=1')
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If API request fails after retries
        """
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Fetching data from {url}")
        
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Successfully fetched data from {endpoint}")
        return data

    def save_json(self, data: Dict, name: str) -> str:
        """Save JSON data to a timestamped file.
        
        Args:
            data: Dictionary to serialize as JSON
            name: Name prefix for the output file (e.g., 'schedule')
            
        Returns:
            Path to the saved JSON file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mlb_{name}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        logger.info(f"Saved raw JSON {name} to {filepath}")
        return filepath

    def run(self) -> Dict[str, Optional[str]]:
        """Execute scraping for all configured endpoints.
        
        Returns:
            Dictionary mapping endpoint names to saved JSON file paths.
            Values are None if scraping failed for that endpoint.
        """
        filepaths: Dict[str, Optional[str]] = {}
        for name, endpoint in self.endpoints.items():
            try:
                data = self.fetch_data(endpoint)
                filepath = self.save_json(data, name)
                filepaths[name] = filepath
            except Exception as e:
                logger.error(f"Scraper failed for {name}: {e}", exc_info=True)
                filepaths[name] = None
        return filepaths
