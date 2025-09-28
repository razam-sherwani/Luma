"""
Django management command to generate hardcoded medical research
"""
from django.core.management.base import BaseCommand
from core.research_generator import SimplifiedResearchGenerator
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate hardcoded medical research data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--specialty',
            type=str,
            help='Specific specialty to generate (optional)',
        )
        parser.add_argument(
            '--max-results',
            type=int,
            default=10,
            help='Maximum results to generate (default: 10)',
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting Hardcoded Medical Research Generation...")
        
        generator = SimplifiedResearchGenerator()
        
        if options['specialty']:
            # Generate specific specialty
            self.stdout.write(f"Generating research for {options['specialty']}...")
            result = generator.update_research_database()
        else:
            # Generate all specialties
            self.stdout.write("Generating research for all specialties...")
            result = generator.update_research_database()
        
        # Display results
        self.stdout.write(f"Generated {result.get('created', 0)} new research articles")
        self.stdout.write(f"Updated {result.get('updated', 0)} existing articles")
        self.stdout.write(f"Total articles in database: {result.get('total', 0)}")
        
        self.stdout.write(self.style.SUCCESS("Hardcoded medical research generation complete!"))