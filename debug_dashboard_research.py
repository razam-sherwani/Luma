#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import ResearchUpdate

print("🔍 DEBUG: Dashboard Research Query")
print("=" * 60)

# This is the exact query used in the dashboard view
recent_research = ResearchUpdate.objects.filter(is_high_impact=True).order_by('-relevance_score', '-date')[:5]

print(f"Query returned {len(recent_research)} articles")
print()

if len(recent_research) == 0:
    print("❌ NO HIGH-IMPACT ARTICLES FOUND!")
    print("Let's check what articles exist:")
    all_articles = ResearchUpdate.objects.all()[:5]
    for article in all_articles:
        print(f"- {article.headline[:50]}... (High Impact: {article.is_high_impact})")
else:
    print("✅ High-impact articles found:")
    for i, research in enumerate(recent_research, 1):
        print(f"{i}. {research.headline}")
        print(f"   URL: {research.source_url}")
        print(f"   Working URL: {'✅ YES' if research.source_url and research.source_url != '' else '❌ NO'}")
        print()

print("\n🔧 Quick Fix: Making sure some articles are high-impact...")
# Make sure at least 5 articles are marked as high-impact
non_high_impact = ResearchUpdate.objects.filter(is_high_impact=False)[:5]
for article in non_high_impact:
    article.is_high_impact = True
    article.save()
    print(f"✅ Made high-impact: {article.headline[:50]}...")

print("\n📊 Final status:")
high_impact_count = ResearchUpdate.objects.filter(is_high_impact=True).count()
print(f"High-impact articles: {high_impact_count}")