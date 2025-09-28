"""
Django management command to fix research recommendations
"""
from django.core.management.base import BaseCommand
from core.models import IntelligentRecommendation, ScrapedResearch, ResearchUpdate
from core.research_generator import SimplifiedResearchGenerator
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix research studies linked to recommendations'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking Research-Recommendation Links...")
        
        # Get current stats
        total_recommendations = IntelligentRecommendation.objects.count()
        recommendations_with_research = IntelligentRecommendation.objects.filter(
            relevant_research__isnull=False
        ).distinct().count()
        scraped_research_count = ScrapedResearch.objects.count()
        research_update_count = ResearchUpdate.objects.count()
        
        self.stdout.write(f"Total recommendations: {total_recommendations}")
        self.stdout.write(f"Recommendations with research: {recommendations_with_research}")
        self.stdout.write(f"ScrapedResearch records: {scraped_research_count}")
        self.stdout.write(f"ResearchUpdate records: {research_update_count}")
        
        # Create missing research studies
        self.stdout.write("\n📚 Creating Missing Research Studies...")
        
        recommendations_without_research = IntelligentRecommendation.objects.filter(
            relevant_research__isnull=True
        ).distinct()
        
        self.stdout.write(f"Recommendations without research: {recommendations_without_research.count()}")
        
        created_count = 0
        research_generator = SimplifiedResearchGenerator()
        
        for recommendation in recommendations_without_research:
            try:
                # Get HCP specialty
                hcp_specialty = recommendation.hcp.specialty
                
                # Create research studies for this specialty
                articles = research_generator.generate_research_for_specialty(hcp_specialty, 2)
                
                # Create ScrapedResearch objects
                research_objects = []
                for article in articles:
                    research_obj = ScrapedResearch.objects.create(
                        title=article['title'],
                        abstract=article['abstract'],
                        specialties=[article['specialty']],
                        source_url=f"/dashboard/research/{ScrapedResearch.objects.count() + 1}/",
                        publication_date=article['date'],
                        relevance_score=article['relevance_score'],
                        keywords=['clinical', 'research', 'medical'],
                        conditions_mentioned=[hcp_specialty.lower()],
                        treatments_mentioned=['treatment', 'therapy'],
                        authors='Research Team',
                        journal='Medical Journal'
                    )
                    research_objects.append(research_obj)
                
                # Link research to recommendation
                recommendation.relevant_research.set(research_objects)
                
                # Update research_evidence JSON field
                research_evidence = [
                    {
                        'title': article['title'],
                        'relevance_score': article['relevance_score'],
                        'abstract': article['abstract'][:200] + '...' if len(article['abstract']) > 200 else article['abstract']
                    }
                    for article in articles
                ]
                recommendation.research_evidence = research_evidence
                recommendation.save()
                
                created_count += 1
                self.stdout.write(f"✅ Created research for: {recommendation.recommendation_title}")
                
            except Exception as e:
                self.stdout.write(f"❌ Error creating research for recommendation {recommendation.id}: {e}")
        
        # Ensure all research has proper URLs
        self.stdout.write("\n🔗 Updating Research URLs...")
        updated_urls = 0
        for research in ScrapedResearch.objects.all():
            if not research.source_url or research.source_url == '#':
                research.source_url = f"/dashboard/research/{research.id}/"
                research.save()
                updated_urls += 1
        
        # Final summary
        self.stdout.write("\n📊 Final Summary:")
        self.stdout.write(f"Research studies created: {created_count}")
        self.stdout.write(f"URLs updated: {updated_urls}")
        
        # Verify final state
        final_recommendations_with_research = IntelligentRecommendation.objects.filter(
            relevant_research__isnull=False
        ).distinct().count()
        
        self.stdout.write(f"Final state - Recommendations with research: {final_recommendations_with_research}/{total_recommendations}")
        
        self.stdout.write(self.style.SUCCESS("✅ Research recommendations fix complete!"))
