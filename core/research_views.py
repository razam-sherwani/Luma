"""
Research Detail View and Auto-Update Functionality
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import ResearchUpdate, UserProfile
from .research_generator import SimplifiedResearchGenerator
import logging

logger = logging.getLogger(__name__)

@login_required
def research_detail(request, research_id):
    """Display detailed view of a research update"""
    research = get_object_or_404(ResearchUpdate, id=research_id)
    
    # Get user profile for personalized recommendations
    user_profile = getattr(request.user, 'userprofile', None)
    
    # Get related research based on specialty
    related_research = ResearchUpdate.objects.filter(
        specialty=research.specialty
    ).exclude(id=research.id).order_by('-relevance_score', '-date')[:5]
    
    context = {
        'research': research,
        'related_research': related_research,
        'user_profile': user_profile,
    }
    
    return render(request, 'core/research_detail.html', context)

@login_required 
def get_research_by_specialty(request):
    """AJAX endpoint to get research filtered by specialty"""
    specialty = request.GET.get('specialty', '')
    impact = request.GET.get('impact', '')
    limit = int(request.GET.get('limit', 10))
    
    # Start with base queryset
    research = ResearchUpdate.objects.all()
    
    # Apply filters
    if specialty:
        research = research.filter(specialty=specialty)
    
    if impact == 'high':
        research = research.filter(is_high_impact=True)
    elif impact == 'normal':
        research = research.filter(is_high_impact=False)
    
    # Order and limit results
    research = research.order_by('-relevance_score', '-date')[:limit]
    
    data = []
    for r in research:
        data.append({
            'id': r.id,
            'headline': r.headline,
            'specialty': r.specialty,
            'date': r.date.strftime('%Y-%m-%d'),
            'abstract': r.abstract[:200] + '...' if r.abstract and len(r.abstract) > 200 else r.abstract,
            'source': r.source,
            'relevance_score': r.relevance_score,
            'is_high_impact': r.is_high_impact,
        })
    
    return JsonResponse({'research': data})

@require_http_methods(["POST"])
@login_required
def trigger_research_update(request):
    """Manual trigger for research update (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        generator = SimplifiedResearchGenerator()
        result = generator.update_all_specialties()
        
        return JsonResponse({
            'success': True,
            'message': 'Research database updated successfully',
            'stats': result
        })
        
    except Exception as e:
        logger.error(f"Manual research update failed: {e}")
        return JsonResponse({
            'error': f'Update failed: {str(e)}'
        }, status=500)

@login_required
def research_dashboard(request):
    """Comprehensive research dashboard"""
    user_profile = getattr(request.user, 'userprofile', None)
    
    # Get personalized research
    research_generator = SimplifiedResearchGenerator()
    
    if user_profile and user_profile.specialty:
        personalized_research = research_generator.get_personalized_research(
            user_profile.specialty, 15
        )
    else:
        personalized_research = ResearchUpdate.objects.filter(
            is_high_impact=True
        ).order_by('-relevance_score', '-date')[:15]
    
    # Get specialty statistics
    from django.db.models import Count, Avg
    specialty_stats = ResearchUpdate.objects.values('specialty').annotate(
        count=Count('specialty'),
        avg_relevance=Avg('relevance_score')
    ).order_by('-count')
    
    # Get recent high-impact research
    high_impact_research = ResearchUpdate.objects.filter(
        is_high_impact=True
    ).order_by('-date')[:10]
    
    # Get available specialties for filtering (using proper aggregation)
    from django.db.models import Count
    specialty_data = ResearchUpdate.objects.values('specialty').annotate(
        count=Count('specialty')
    ).order_by('specialty')
    specialties = [item['specialty'] for item in specialty_data]
    
    context = {
        'personalized_research': personalized_research,
        'high_impact_research': high_impact_research,
        'specialty_stats': specialty_stats,
        'specialties': specialties,
        'user_profile': user_profile,
        'total_research': ResearchUpdate.objects.count(),
    }
    
    return render(request, 'core/research_dashboard.html', context)