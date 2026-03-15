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
    filepaths = scraper.run()
    logger.info(f"Scraper completed. Outputs: {filepaths}")
    
    logger.info("Pipeline Execution Summary:")
    for name, json_path in filepaths.items():
        if json_path:
            transformer = DataTransformer(json_path)
            csv_path, xml_path = transformer.run()
            logger.info(f"[{name}] Extracted to CSV: {csv_path}")
            if xml_path:
                logger.info(f"[{name}] Extracted to XML: {xml_path}")

if __name__ == "__main__":
    main()
