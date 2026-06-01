import logging
from typing import Dict
from src.config import settings
from src.scraper import MLBScraper
from src.transformer import DataTransformer

logger: logging.Logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main() -> None:
    """Execute the MLB data pipeline: scrape, transform, and export data."""
    setup_logging()
    
    logger.info("Starting MLB Pipeline")
    
    try:
        scraper = MLBScraper()
        filepaths: Dict[str, str] = scraper.run()
        logger.info(f"Scraper completed. Outputs: {filepaths}")
        
        logger.info("Pipeline Execution Summary:")
        successful_transforms = 0
        
        for name, json_path in filepaths.items():
            if json_path:
                try:
                    transformer = DataTransformer(json_path)
                    csv_path, xml_path = transformer.run()
                    logger.info(f"[{name}] Extracted to CSV: {csv_path}")
                    if xml_path:
                        logger.info(f"[{name}] Extracted to XML: {xml_path}")
                    successful_transforms += 1
                except Exception as e:
                    logger.error(f"[{name}] Transformation failed: {e}", exc_info=True)
            else:
                logger.warning(f"[{name}] No JSON output from scraper")
        
        logger.info(f"Pipeline complete. {successful_transforms}/{len(filepaths)} transformations successful.")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
