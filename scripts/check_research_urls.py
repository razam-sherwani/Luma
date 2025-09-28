#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import ResearchUpdate

print("=== Recent High-Impact Research Articles with URLs ===")
recent_research = ResearchUpdate.objects.filter(is_high_impact=True).order_by('-relevance_score', '-date')[:5]

for i, research in enumerate(recent_research, 1):
    print(f"\n{i}. Title: {research.headline}")
    print(f"   Specialty: {research.specialty}")
    print(f"   Date: {research.date}")
    print(f"   Source: {research.source}")
    print(f"   URL: {research.source_url}")
    print(f"   Impact: {'High' if research.is_high_impact else 'Normal'}")
    print("-" * 80)

print(f"\nTotal research articles: {ResearchUpdate.objects.count()}")
print(f"High-impact articles: {ResearchUpdate.objects.filter(is_high_impact=True).count()}")
print(f"Articles with URLs: {ResearchUpdate.objects.exclude(source_url='').count()}")