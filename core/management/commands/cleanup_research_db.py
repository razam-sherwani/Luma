"""
Clean up research database to fix specialty duplicates
"""
from django.core.management.base import BaseCommand
from core.models import ResearchUpdate
from django.db.models import Count

class Command(BaseCommand):
    help = 'Clean up research database specialties'

    def handle(self, *args, **options):
        self.stdout.write('🧹 CLEANING RESEARCH DATABASE')
        self.stdout.write('=' * 40)
        
        # Check current state
        total_before = ResearchUpdate.objects.count()
        specialties_before = ResearchUpdate.objects.values_list('specialty', flat=True).distinct()
        unique_specialties_before = len(set(specialties_before))
        
        self.stdout.write(f'Before cleanup:')
        self.stdout.write(f'  Total articles: {total_before}')
        self.stdout.write(f'  Raw distinct count: {len(specialties_before)}')
        self.stdout.write(f'  Actual unique specialties: {unique_specialties_before}')
        
        # Show actual unique specialties
        unique_specs = sorted(list(set(specialties_before)))
        self.stdout.write(f'\nActual unique specialties ({len(unique_specs)}):')
        for spec in unique_specs:
            count = ResearchUpdate.objects.filter(specialty=spec).count()
            self.stdout.write(f'  - {spec}: {count} articles')
        
        # Remove any truly duplicate articles (same headline and specialty)
        duplicates_removed = 0
        seen_articles = set()
        
        for article in ResearchUpdate.objects.all():
            article_key = (article.headline, article.specialty)
            if article_key in seen_articles:
                article.delete()
                duplicates_removed += 1
            else:
                seen_articles.add(article_key)
        
        # Final count
        total_after = ResearchUpdate.objects.count()
        specialties_after = sorted(list(set(ResearchUpdate.objects.values_list('specialty', flat=True))))
        
        self.stdout.write(f'\nAfter cleanup:')
        self.stdout.write(f'  Total articles: {total_after}')
        self.stdout.write(f'  Unique specialties: {len(specialties_after)}')
        self.stdout.write(f'  Duplicates removed: {duplicates_removed}')
        
        self.stdout.write(f'\n✅ Database cleanup complete!')
        self.stdout.write('The specialty dropdown should now show unique values only.')