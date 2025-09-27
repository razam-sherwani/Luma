"""
Django management command to update medical research automatically
Usage: python manage.py update_research
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.research_generator import SimplifiedResearchGenerator
from core.research_scraper import MedicalResearchScraper
import logging

class Command(BaseCommand):
    help = 'Update medical research database with latest research articles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if recently updated',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output',
        )
        parser.add_argument(
            '--mode',
            choices=['simple', 'advanced'],
            default='simple',
            help='Choose between simple generation or advanced web scraping',
        )

    def handle(self, *args, **options):
        if options['verbose']:
            logging.basicConfig(level=logging.INFO)
        
        self.stdout.write(
            self.style.SUCCESS('Starting medical research update...')
        )

        try:
            if options['mode'] == 'advanced':
                self.stdout.write("Using advanced web scraping mode...")
                scraper = MedicalResearchScraper()
                result = scraper.update_research_database()
            else:
                self.stdout.write("Using simple generation mode...")
                generator = SimplifiedResearchGenerator()
                result = generator.update_all_specialties()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Research update completed successfully!"
                )
            )
            self.stdout.write(f"📊 Statistics:")
            self.stdout.write(f"   • Deleted old articles: {result['deleted_old']}")
            self.stdout.write(f"   • Created new articles: {result['created_new']}")
            self.stdout.write(f"   • Updated existing: {result['updated_existing']}")
            self.stdout.write(f"   • Total articles in DB: {result['total_articles']}")
            
            self.stdout.write(f"🏥 Specialty Distribution:")
            for specialty, count in result['specialty_distribution'].items():
                self.stdout.write(f"   • {specialty}: {count} articles")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Research update failed: {str(e)}')
            )
            raise e