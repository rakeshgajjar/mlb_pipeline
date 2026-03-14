import logging
from src.config import settings
from src.scraper import MLBScraper
from src.transformer import DataTransformer

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting MLB Pipeline")
    
    scraper = MLBScraper()
    json_path = scraper.run()
    logger.info(f"Scraper completed. Output: {json_path}")
    
    transformer = DataTransformer(json_path)
    csv_path, xml_path = transformer.run()
    
    logger.info("Pipeline Execution Summary:")
    logger.info(f"JSON: {json_path}")
    logger.info(f"CSV:  {csv_path}")
    logger.info(f"XML:  {xml_path}")

if __name__ == "__main__":
    main()
