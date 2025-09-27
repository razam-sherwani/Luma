from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from .models import HCP, ResearchUpdate, EMRData, Engagement

@login_required
def dashboard(request):
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
    
    context = {
        'overdue_hcps': overdue_hcps,
        'recent_research': recent_research,
        'recent_emr_data': recent_emr_data,
    }
    return render(request, 'core/dashboard.html', context)

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
