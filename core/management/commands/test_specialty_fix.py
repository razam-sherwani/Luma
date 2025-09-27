"""
Test script to verify specialty dropdown fix
"""
from django.core.management.base import BaseCommand
from core.models import ResearchUpdate
from django.db.models import Count

class Command(BaseCommand):
    help = 'Test the specialty dropdown fix'

    def handle(self, *args, **options):
        self.stdout.write('🔍 TESTING SPECIALTY DROPDOWN FIX')
        self.stdout.write('=' * 50)
        
        # Method 1: Old problematic way (values_list distinct)
        old_way = ResearchUpdate.objects.values_list('specialty', flat=True).distinct()
        self.stdout.write(f'\n❌ Old method (values_list distinct):')
        self.stdout.write(f'   Count: {len(old_way)} (should be 10)')
        
        # Method 2: New fixed way (values with annotation)
        new_way = ResearchUpdate.objects.values('specialty').annotate(
            count=Count('specialty')
        ).order_by('specialty')
        specialties_new = [item['specialty'] for item in new_way]
        
        self.stdout.write(f'\n✅ New method (values with annotation):')
        self.stdout.write(f'   Count: {len(specialties_new)} (should be 10)')
        
        self.stdout.write(f'\n📝 UNIQUE SPECIALTIES FOR DROPDOWN:')
        for i, item in enumerate(new_way, 1):
            self.stdout.write(f'   {i:2d}. {item["specialty"]} ({item["count"]} articles)')
        
        # Method 3: Python set deduplication
        python_set = list(set(ResearchUpdate.objects.values_list('specialty', flat=True)))
        self.stdout.write(f'\n🐍 Python set method:')
        self.stdout.write(f'   Count: {len(python_set)} (should be 10)')
        
        # Verify the fix
        if len(specialties_new) == 10:
            self.stdout.write(f'\n🎉 SUCCESS: Dropdown will show {len(specialties_new)} unique specialties!')
            self.stdout.write('   No more duplicates in the research dashboard dropdown.')
        else:
            self.stdout.write(f'\n❌ ISSUE: Expected 10 specialties, got {len(specialties_new)}')
        
        self.stdout.write('\n📍 To test in browser:')
        self.stdout.write('   1. Go to http://127.0.0.1:8000/accounts/login/')
        self.stdout.write('   2. Login with any HCP credentials')
        self.stdout.write('   3. Navigate to Research Dashboard')
        self.stdout.write('   4. Check the specialty dropdown - should show 10 unique options')