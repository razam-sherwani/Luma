from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from .models import HCP, ResearchUpdate, EMRData, Engagement, UserProfile, HCRRecommendation

@login_required
def dashboard(request):
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'HCR'}  # Default to HCR if not specified
    )
    
    if user_profile.role == 'HCP':
        return hcp_dashboard(request, user_profile)
    else:
        return hcr_dashboard(request, user_profile)

def hcr_dashboard(request, user_profile):
    """Dashboard for Healthcare Representatives"""
    # Get overdue engagements (HCPs not contacted in 30+ days)
    thirty_days_ago = date.today() - timedelta(days=30)
    overdue_hcps = []
    
    for hcp in HCP.objects.all():
        last_engagement = Engagement.objects.filter(hcp=hcp).order_by('-date').first()
        if not last_engagement or last_engagement.date < thirty_days_ago:
            overdue_hcps.append(hcp)
    
    # Get recent research updates
    recent_research = ResearchUpdate.objects.order_by('-date')[:5]
    
    # Get recent EMR flags
    recent_emr_data = EMRData.objects.order_by('-date')[:5]
    
    # Get all HCPs for the HCR overview
    all_hcps = HCP.objects.all()
    
    context = {
        'user_role': 'HCR',
        'overdue_hcps': overdue_hcps,
        'recent_research': recent_research,
        'recent_emr_data': recent_emr_data,
        'all_hcps': all_hcps,
    }
    return render(request, 'core/hcr_dashboard.html', context)

def hcp_dashboard(request, user_profile):
    """Dashboard for Healthcare Providers"""
    # Get all recommendations for this HCP (query not sliced yet)
    all_recommendations_query = HCRRecommendation.objects.filter(
        hcp_user=request.user
    ).order_by('-created_date')
    
    # Count unread recommendations (using the unsliced query)
    unread_count = all_recommendations_query.filter(is_read=False).count()
    
    # Get limited recommendations for display (now slice)
    recommendations = all_recommendations_query[:10]
    
    # Get research relevant to HCP's specialty
    specialty_research = ResearchUpdate.objects.filter(
        specialty=user_profile.specialty
    ).order_by('-date')[:5] if user_profile.specialty else ResearchUpdate.objects.order_by('-date')[:5]
    
    # Get general research updates
    general_research = ResearchUpdate.objects.exclude(
        specialty=user_profile.specialty
    ).order_by('-date')[:3] if user_profile.specialty else []
    
    context = {
        'user_role': 'HCP',
        'user_profile': user_profile,
        'recommendations': recommendations,
        'specialty_research': specialty_research,
        'general_research': general_research,
        'unread_count': unread_count,
    }
    return render(request, 'core/hcp_dashboard.html', context)

@login_required
def mark_recommendation_read(request, recommendation_id):
    """Mark a recommendation as read"""
    recommendation = get_object_or_404(HCRRecommendation, id=recommendation_id, hcp_user=request.user)
    recommendation.is_read = True
    recommendation.save()
    messages.success(request, 'Recommendation marked as read.')
    return redirect('dashboard')

@login_required
def hcp_profile(request, hcp_id):
    hcp = get_object_or_404(HCP, id=hcp_id)
    
    if request.method == 'POST':
        note = request.POST.get('note')
        if note:
            Engagement.objects.create(
                hcp=hcp,
                date=date.today(),
                note=note
            )
            messages.success(request, 'Engagement logged successfully!')
            return redirect('hcp_profile', hcp_id=hcp_id)
    
    engagements = Engagement.objects.filter(hcp=hcp).order_by('-date')
    emr_data = EMRData.objects.filter(hcp=hcp).order_by('-date')
    relevant_research = ResearchUpdate.objects.filter(specialty=hcp.specialty).order_by('-date')
    
    context = {
        'hcp': hcp,
        'engagements': engagements,
        'emr_data': emr_data,
        'relevant_research': relevant_research,
    }
    return render(request, 'core/hcp_profile.html', context)
