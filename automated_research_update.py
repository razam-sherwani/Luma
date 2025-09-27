#!/usr/bin/env python
"""
Automated Research Update Script
Runs daily to update the medical research database
"""
import os
import sys
import django
from pathlib import Path

# Add the project root directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

# Now import Django modules
from core.research_generator import SimplifiedResearchGenerator
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('research_update.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to update research database"""
    logger.info("Starting automated research update...")
    
    try:
        generator = SimplifiedResearchGenerator()
        result = generator.update_all_specialties()
        
        logger.info("Research update completed successfully!")
        logger.info(f"Statistics: {result}")
        
        # Log individual specialty distributions
        for specialty, count in result['specialty_distribution'].items():
            logger.info(f"  {specialty}: {count} articles")
            
    except Exception as e:
        logger.error(f"Research update failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()