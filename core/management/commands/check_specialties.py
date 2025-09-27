"""
Quick command to check specialties in database
"""
from django.core.management.base import BaseCommand
from core.models import ResearchUpdate

class Command(BaseCommand):
    help = 'Check specialties in database for duplicates'

    def handle(self, *args, **options):
        # Use a better approach to get unique specialties
        from django.db.models import Count
        specialty_counts = ResearchUpdate.objects.values('specialty').annotate(
            count=Count('specialty')
        ).order_by('specialty')
        
        specialties = [item['specialty'] for item in specialty_counts]
        
        self.stdout.write(f'Total unique specialties: {len(specialties)}')
        self.stdout.write('\nSpecialties:')
        for item in specialty_counts:
            self.stdout.write(f'  - {repr(item["specialty"])} ({item["count"]} articles)')