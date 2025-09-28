#!/usr/bin/env python
"""
Clean research articles - keep only the two working ones
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import ResearchUpdate

def clean_research_articles():
    """Keep only the minimally invasive ACL and novel beta blocker articles"""
    
    # Get all articles
    all_articles = ResearchUpdate.objects.all()
    print(f"Total articles before cleanup: {all_articles.count()}")
    
    # Find the two articles to keep
    acl_article = ResearchUpdate.objects.filter(
        headline__icontains="Minimally Invasive ACL Reconstruction"
    ).first()
    
    beta_blocker_article = ResearchUpdate.objects.filter(
        headline__icontains="Novel Beta-Blocker Heartguard"
    ).first()
    
    if acl_article:
        print(f"✅ Found ACL article: {acl_article.headline}")
        print(f"   URL: {acl_article.source_url}")
    else:
        print("❌ ACL article not found!")
        
    if beta_blocker_article:
        print(f"✅ Found Beta-blocker article: {beta_blocker_article.headline}")
        print(f"   URL: {beta_blocker_article.source_url}")
    else:
        print("❌ Beta-blocker article not found!")
    
    # Get IDs to keep
    keep_ids = []
    if acl_article:
        keep_ids.append(acl_article.id)
    if beta_blocker_article:
        keep_ids.append(beta_blocker_article.id)
    
    print(f"\nKeeping articles with IDs: {keep_ids}")
    
    # Delete all others
    if keep_ids:
        articles_to_delete = ResearchUpdate.objects.exclude(id__in=keep_ids)
        delete_count = articles_to_delete.count()
        print(f"Deleting {delete_count} articles...")
        
        # Actually delete them
        articles_to_delete.delete()
        
        print(f"✅ Cleanup complete!")
        print(f"Articles remaining: {ResearchUpdate.objects.count()}")
        
        # Show remaining articles
        remaining = ResearchUpdate.objects.all()
        for article in remaining:
            print(f"- {article.headline}")
            print(f"  URL: {article.source_url}")
            print(f"  Specialty: {article.specialty}")
            print()
    else:
        print("❌ No articles found to keep!")

if __name__ == "__main__":
    clean_research_articles()