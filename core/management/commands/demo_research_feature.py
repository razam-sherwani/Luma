"""
Interactive Demo Script for Medical Research Feature
Run this to see the feature in action with sample data
"""
from django.core.management.base import BaseCommand
from core.models import ResearchUpdate, UserProfile
from core.research_generator import SimplifiedResearchGenerator
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Interactive demo of the medical research feature'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎬 MEDICAL RESEARCH FEATURE DEMO'))
        self.stdout.write('=' * 60)
        
        # 1. Show current research statistics
        self.stdout.write('\n📊 CURRENT RESEARCH DATABASE:')
        total_research = ResearchUpdate.objects.count()
        high_impact = ResearchUpdate.objects.filter(is_high_impact=True).count()
        recent_research = ResearchUpdate.objects.filter(
            date__gte=datetime.now().date() - timedelta(days=7)
        ).count()
        
        self.stdout.write(f'   • Total Articles: {total_research}')
        self.stdout.write(f'   • High-Impact Studies: {high_impact}')
        self.stdout.write(f'   • Recent Articles (7 days): {recent_research}')
        
        # 2. Show specialty distribution
        self.stdout.write('\n🏥 RESEARCH BY SPECIALTY:')
        from django.db.models import Count
        specialty_dist = ResearchUpdate.objects.values('specialty').annotate(
            count=Count('specialty')
        ).order_by('-count')[:5]
        
        for item in specialty_dist:
            self.stdout.write(f'   • {item["specialty"]}: {item["count"]} articles')
        
        # 3. Show sample high-impact research
        self.stdout.write('\n🔥 HIGH-IMPACT RESEARCH EXAMPLES:')
        high_impact_samples = ResearchUpdate.objects.filter(
            is_high_impact=True
        ).order_by('-relevance_score')[:3]
        
        for i, research in enumerate(high_impact_samples, 1):
            self.stdout.write(f'\n   {i}. {research.headline}')
            self.stdout.write(f'      Specialty: {research.specialty}')
            self.stdout.write(f'      Relevance: ⭐ {research.relevance_score:.1f}/1.0')
            self.stdout.write(f'      Date: {research.date.strftime("%B %d, %Y")}')
            self.stdout.write(f'      Source: {research.source}')
            if research.abstract:
                abstract_preview = research.abstract[:100] + '...'
                self.stdout.write(f'      Abstract: {abstract_preview}')
        
        # 4. Show personalization example
        self.stdout.write('\n👨‍⚕️ PERSONALIZATION EXAMPLE:')
        sample_user = UserProfile.objects.filter(specialty__isnull=False).first()
        if sample_user:
            self.stdout.write(f'   Doctor: {sample_user.user.get_full_name() or sample_user.user.username}')
            self.stdout.write(f'   Specialty: {sample_user.specialty}')
            
            # Get personalized research
            generator = SimplifiedResearchGenerator()
            personalized = generator.get_personalized_research(sample_user.specialty, 5)
            
            self.stdout.write(f'\n   Personalized Research for {sample_user.specialty}:')
            for i, research in enumerate(personalized[:3], 1):
                relevance_stars = '⭐' * int(research.relevance_score * 5)
                impact_badge = ' 🔥' if research.is_high_impact else ''
                self.stdout.write(f'   {i}. {research.headline[:60]}...{impact_badge}')
                self.stdout.write(f'      {relevance_stars} ({research.relevance_score:.1f}) • {research.date.strftime("%b %d")}')
        
        # 5. Show filtering capabilities
        self.stdout.write('\n🔍 FILTERING DEMONSTRATION:')
        cardiology_research = ResearchUpdate.objects.filter(
            specialty='CARDIOVASCULAR DISEASE (CARDIOLOGY)'
        ).count()
        internal_med_research = ResearchUpdate.objects.filter(
            specialty='INTERNAL MEDICINE'
        ).count()
        
        self.stdout.write(f'   • Cardiology Research: {cardiology_research} articles')
        self.stdout.write(f'   • Internal Medicine Research: {internal_med_research} articles')
        self.stdout.write('   • Filters available: Specialty, Impact Level, Date Range')
        
        # 6. Show automation features
        self.stdout.write('\n🤖 AUTOMATION FEATURES:')
        self.stdout.write('   • Daily Updates: Automatic research generation')
        self.stdout.write('   • Smart Categorization: AI-powered specialty matching')
        self.stdout.write('   • Quality Scoring: Relevance calculation for each article')
        self.stdout.write('   • Content Cleanup: Removes articles older than 30 days')
        self.stdout.write('   • Windows Scheduler: Ready for production automation')
        
        # 7. Show user experience flow
        self.stdout.write('\n📱 USER EXPERIENCE FLOW:')
        self.stdout.write('   1. Login → Dashboard → Research Button')
        self.stdout.write('   2. View personalized research feed')
        self.stdout.write('   3. Filter by specialty or impact level')
        self.stdout.write('   4. Click article headlines for full details')
        self.stdout.write('   5. Access related research suggestions')
        self.stdout.write('   6. Share findings with colleagues')
        
        # 8. Show technical capabilities
        self.stdout.write('\n⚙️ TECHNICAL CAPABILITIES:')
        self.stdout.write('   • Real-time AJAX filtering')
        self.stdout.write('   • Responsive design for all devices')
        self.stdout.write('   • Admin controls for manual updates')
        self.stdout.write('   • Comprehensive error handling')
        self.stdout.write('   • Production-ready performance')
        
        # 9. Generate sample research if needed
        if total_research < 10:
            self.stdout.write('\n🔧 GENERATING SAMPLE RESEARCH...')
            generator = SimplifiedResearchGenerator()
            result = generator.update_all_specialties()
            self.stdout.write(f'   Generated {result["created_new"]} new articles')
        
        # 10. Show next steps
        self.stdout.write('\n🎯 HOW TO USE THIS FEATURE:')
        self.stdout.write('   1. Start Django server: python manage.py runserver')
        self.stdout.write('   2. Login to Pulse')
        self.stdout.write('   3. Navigate to Research Dashboard')
        self.stdout.write('   4. Explore personalized research articles')
        self.stdout.write('   5. Use filters to find specific content')
        self.stdout.write('   6. Click articles to read full details')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('🚀 DEMO COMPLETE! Ready to explore the research feature!'))
        self.stdout.write('📖 See RESEARCH_FEATURE_USER_GUIDE.md for detailed instructions')
        self.stdout.write('⚡ See QUICK_START_RESEARCH_GUIDE.md for quick reference')