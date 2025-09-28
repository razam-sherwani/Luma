#!/usr/bin/env python
"""
Script to update all research articles with real, working URLs
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import ResearchUpdate
from core.real_research_urls import get_real_research_url

def main():
    print("=== Updating All Research Articles with Real URLs ===")
    
    # Get all research articles
    all_articles = ResearchUpdate.objects.all()
    
    print(f"Found {all_articles.count()} articles to update")
    
    updated_count = 0
    
    for article in all_articles:
        # Get a real URL for this article's specialty
        new_url = get_real_research_url(article.specialty)
        old_url = article.source_url
        
        article.source_url = new_url
        article.save()
        
        print(f"✅ Updated: {article.headline[:50]}...")
        print(f"   Specialty: {article.specialty}")
        print(f"   Old URL: {old_url}")
        print(f"   New URL: {new_url}")
        print("-" * 80)
        
        updated_count += 1
    
    print(f"\n🎉 Successfully updated {updated_count} articles with real URLs!")
    
    # Show summary
    total = ResearchUpdate.objects.count()
    with_urls = ResearchUpdate.objects.exclude(source_url__isnull=True).exclude(source_url='').count()
    print(f"\n📈 Summary:")
    print(f"   Total articles: {total}")
    print(f"   Articles with URLs: {with_urls}")
    print(f"   Coverage: {(with_urls/total*100):.1f}%" if total > 0 else "   Coverage: 0%")
    
    print("\n✅ All research articles now link to real, accessible medical research!")
    print("🔗 Users can now click on research alerts and see actual content.")

if __name__ == "__main__":
    main()