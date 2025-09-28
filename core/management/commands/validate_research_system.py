"""
System Validation and Error Checking for Pulse Research System
"""
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import connections
from django.db import models
from django.urls import reverse
from core.models import ResearchUpdate, UserProfile, HCP
from core.research_generator import SimplifiedResearchGenerator
from core.research_scraper import MedicalResearchScraper
import logging

class Command(BaseCommand):
    help = 'Validate the research system and check for errors'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix detected issues',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Starting Research System Validation...'))
        
        errors = []
        warnings = []
        fixes_applied = []
        
        # 1. Database connectivity
        try:
            db_conn = connections['default']
            db_conn.cursor()
            self.stdout.write('✅ Database connection: OK')
        except Exception as e:
            errors.append(f'Database connection failed: {e}')
        
        # 2. Model validation
        try:
            ResearchUpdate.objects.first()
            self.stdout.write('✅ ResearchUpdate model: OK')
        except Exception as e:
            errors.append(f'ResearchUpdate model error: {e}')
        
        # 3. Research data validation
        try:
            total_research = ResearchUpdate.objects.count()
            high_impact = ResearchUpdate.objects.filter(is_high_impact=True).count()
            recent_research = ResearchUpdate.objects.filter(
                date__gte='2025-09-01'
            ).count()
            
            self.stdout.write(f'✅ Research data: {total_research} total, {high_impact} high-impact, {recent_research} recent')
            
            if total_research == 0:
                warnings.append('No research articles found')
                if options['fix']:
                    self.stdout.write('🔧 Generating initial research data...')
                    generator = SimplifiedResearchGenerator()
                    result = generator.update_all_specialties()
                    fixes_applied.append(f'Generated {result["created_new"]} research articles')
            
        except Exception as e:
            errors.append(f'Research data validation failed: {e}')
        
        # 4. URL pattern validation
        try:
            urls_to_test = [
                'research_dashboard',
                'research_by_specialty',
                'trigger_research_update'
            ]
            
            for url_name in urls_to_test:
                try:
                    if url_name == 'research_detail':
                        reverse(url_name, args=[1])
                    else:
                        reverse(url_name)
                    self.stdout.write(f'✅ URL {url_name}: OK')
                except Exception as e:
                    errors.append(f'URL {url_name} failed: {e}')
                    
        except Exception as e:
            errors.append(f'URL validation failed: {e}')
        
        # 5. Template validation
        try:
            from django.template.loader import get_template
            templates_to_test = [
                'core/research_dashboard.html',
                'core/research_detail.html'
            ]
            
            for template_name in templates_to_test:
                try:
                    get_template(template_name)
                    self.stdout.write(f'✅ Template {template_name}: OK')
                except Exception as e:
                    errors.append(f'Template {template_name} failed: {e}')
                    
        except Exception as e:
            errors.append(f'Template validation failed: {e}')
        
        # 6. Research generator validation
        try:
            generator = SimplifiedResearchGenerator()
            test_research = generator.generate_research_for_specialty('INTERNAL MEDICINE', 1)
            if test_research and len(test_research) > 0:
                self.stdout.write('✅ Research generator: OK')
            else:
                warnings.append('Research generator returned no results')
        except Exception as e:
            errors.append(f'Research generator failed: {e}')
        
        # 7. User profile validation
        try:
            total_users = UserProfile.objects.count()
            users_with_specialty = UserProfile.objects.exclude(specialty__isnull=True).exclude(specialty='').count()
            self.stdout.write(f'✅ User profiles: {total_users} total, {users_with_specialty} with specialty')
            
            if users_with_specialty == 0:
                warnings.append('No users have specialties assigned')
                
        except Exception as e:
            errors.append(f'User profile validation failed: {e}')
        
        # 8. Research scraper validation (optional)
        try:
            scraper = MedicalResearchScraper()
            self.stdout.write('✅ Research scraper: OK')
        except ImportError as e:
            warnings.append(f'Research scraper dependencies missing: {e}')
        except Exception as e:
            errors.append(f'Research scraper failed: {e}')
        
        # 9. Specialty distribution validation
        try:
            from django.db.models import Count
            specialty_distribution = ResearchUpdate.objects.values('specialty').annotate(
                count=Count('specialty')
            ).order_by('-count')
            
            if specialty_distribution:
                self.stdout.write('✅ Specialty distribution:')
                for item in specialty_distribution[:5]:
                    self.stdout.write(f'   • {item["specialty"]}: {item["count"]} articles')
            else:
                warnings.append('No specialty distribution data available')
                
        except Exception as e:
            errors.append(f'Specialty distribution validation failed: {e}')
        
        # 10. Relevance scoring validation
        try:
            avg_relevance = ResearchUpdate.objects.aggregate(
                avg_score=models.Avg('relevance_score')
            )['avg_score']
            
            if avg_relevance:
                self.stdout.write(f'✅ Average relevance score: {avg_relevance:.2f}')
            else:
                warnings.append('No relevance scores available')
                
        except Exception as e:
            errors.append(f'Relevance scoring validation failed: {e}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 VALIDATION SUMMARY'))
        self.stdout.write('='*50)
        
        if not errors and not warnings:
            self.stdout.write(self.style.SUCCESS('🎉 All systems operational! No issues detected.'))
        else:
            if errors:
                self.stdout.write(self.style.ERROR(f'❌ {len(errors)} ERROR(S) DETECTED:'))
                for error in errors:
                    self.stdout.write(f'   • {error}')
            
            if warnings:
                self.stdout.write(self.style.WARNING(f'⚠️  {len(warnings)} WARNING(S):'))
                for warning in warnings:
                    self.stdout.write(f'   • {warning}')
            
            if fixes_applied:
                self.stdout.write(self.style.SUCCESS(f'🔧 {len(fixes_applied)} FIX(ES) APPLIED:'))
                for fix in fixes_applied:
                    self.stdout.write(f'   • {fix}')
        
        # Exit with error code if critical errors found
        if errors:
            raise Exception(f'System validation failed with {len(errors)} error(s)')