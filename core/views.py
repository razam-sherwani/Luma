from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from .models import HCP, ResearchUpdate, EMRData, Engagement, UserProfile, HCRRecommendation, PatientCohort, TreatmentOutcome, CohortRecommendation, ActionableInsight

def generate_actionable_insights():
    """Generate intelligent insights for HCRs based on data analysis"""
    insights = []
    
    # Get all HCPs
    hcps = HCP.objects.all()
    
    for hcp in hcps:
        # Check for missing standard-of-care treatments
        if hcp.specialty == 'Oncology':
            # Simulate analysis - in real app, this would analyze EMR data
            if not ActionableInsight.objects.filter(hcp=hcp, insight_type='MISSING_TREATMENT').exists():
                insight = ActionableInsight.objects.create(
                    hcp=hcp,
                    insight_type='MISSING_TREATMENT',
                    title='Immunotherapy Underutilization Detected',
                    description=f'Dr. {hcp.name} has 15+ patients with advanced melanoma who could benefit from new immunotherapy protocols. Current treatment patterns show 60% are on older regimens.',
                    priority_score=85,
                    patient_impact=15
                )
                insights.append(insight)
        
        elif hcp.specialty == 'Cardiology':
            if not ActionableInsight.objects.filter(hcp=hcp, insight_type='TREATMENT_GAP').exists():
                insight = ActionableInsight.objects.create(
                    hcp=hcp,
                    insight_type='TREATMENT_GAP',
                    title='Cardiac Stent Technology Gap',
                    description=f'Dr. {hcp.name} performs 20+ stent procedures monthly but may not be using latest biodegradable stent technology that reduces restenosis by 40%.',
                    priority_score=75,
                    patient_impact=20
                )
                insights.append(insight)
        
        elif hcp.specialty == 'Endocrinology':
            if not ActionableInsight.objects.filter(hcp=hcp, insight_type='PATIENT_COHORT').exists():
                insight = ActionableInsight.objects.create(
                    hcp=hcp,
                    insight_type='PATIENT_COHORT',
                    title='Diabetes Management Optimization Opportunity',
                    description=f'Dr. {hcp.name} has 50+ Type 2 diabetes patients. New continuous glucose monitoring shows 40% better control rates.',
                    priority_score=80,
                    patient_impact=50
                )
                insights.append(insight)
    
    return insights

def generate_cohort_recommendations():
    """Generate recommendations based on patient cohort analysis"""
    recommendations = []
    
    # Get or create sample patient cohorts
    cohorts_data = [
        {
            'name': 'Advanced Melanoma Patients',
            'description': 'Patients with stage III/IV melanoma requiring aggressive treatment',
            'condition': 'Advanced Melanoma',
            'specialty': 'Oncology',
            'patient_count': 25
        },
        {
            'name': 'Type 2 Diabetes with Complications',
            'description': 'Diabetic patients with neuropathy, nephropathy, or retinopathy',
            'condition': 'Type 2 Diabetes with Complications',
            'specialty': 'Endocrinology',
            'patient_count': 40
        },
        {
            'name': 'High-Risk Cardiac Patients',
            'description': 'Patients with multiple cardiac risk factors requiring intervention',
            'condition': 'High-Risk Cardiovascular Disease',
            'specialty': 'Cardiology',
            'patient_count': 30
        }
    ]
    
    for cohort_data in cohorts_data:
        cohort, created = PatientCohort.objects.get_or_create(
            name=cohort_data['name'],
            defaults=cohort_data
        )
        
        if created:
            # Add treatment outcomes for new cohorts
            if cohort.condition == 'Advanced Melanoma':
                TreatmentOutcome.objects.create(
                    cohort=cohort,
                    treatment_name='PD-1 Inhibitor (Pembrolizumab)',
                    success_rate=70.0,
                    side_effects='Mild fatigue, rash in 20% of patients',
                    notes='Best outcomes in patients with high PD-L1 expression'
                )
                TreatmentOutcome.objects.create(
                    cohort=cohort,
                    treatment_name='Combination Immunotherapy',
                    success_rate=85.0,
                    side_effects='More severe but manageable with proper monitoring',
                    notes='IPI + NIVO combination shows superior results'
                )
            
            elif cohort.condition == 'Type 2 Diabetes with Complications':
                TreatmentOutcome.objects.create(
                    cohort=cohort,
                    treatment_name='Continuous Glucose Monitoring + SGLT2 Inhibitor',
                    success_rate=65.0,
                    side_effects='Minimal - occasional UTI risk',
                    notes='Reduces progression of complications by 40%'
                )
            
            elif cohort.condition == 'High-Risk Cardiovascular Disease':
                TreatmentOutcome.objects.create(
                    cohort=cohort,
                    treatment_name='Biodegradable Drug-Eluting Stent',
                    success_rate=90.0,
                    side_effects='Standard stent placement risks',
                    notes='Reduces restenosis by 40% compared to traditional stents'
                )
    
    # Generate recommendations for HCPs
    hcps = HCP.objects.all()
    cohorts = PatientCohort.objects.all()
    
    for hcp in hcps:
        for cohort in cohorts:
            if hcp.specialty == cohort.specialty:
                # Check if recommendation already exists
                if not CohortRecommendation.objects.filter(hcp=hcp, cohort=cohort).exists():
                    best_treatment = cohort.treatment_outcomes.order_by('-success_rate').first()
                    
                    if best_treatment:
                        recommendation = CohortRecommendation.objects.create(
                            hcp=hcp,
                            cohort=cohort,
                            treatment_outcome=best_treatment,
                            title=f'Optimize Treatment for {cohort.condition}',
                            message=f'Your {cohort.patient_count} patients with {cohort.condition} could benefit from {best_treatment.treatment_name}. Success rate: {best_treatment.success_rate}%. {best_treatment.notes}',
                            priority='HIGH' if best_treatment.success_rate > 80 else 'MEDIUM'
                        )
                        recommendations.append(recommendation)
    
    return recommendations

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
    """Dashboard for Healthcare Representatives with intelligent insights"""
    # Generate actionable insights and cohort recommendations
    generate_actionable_insights()
    generate_cohort_recommendations()
    
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
    
    # Get high-priority actionable insights (sorted by priority score)
    actionable_insights = ActionableInsight.objects.filter(
        is_addressed=False
    ).order_by('-priority_score', '-created_date')[:6]
    
    # Get patient cohorts for overview
    patient_cohorts = PatientCohort.objects.all()[:3]
    
    # Get cohort recommendations
    cohort_recommendations = CohortRecommendation.objects.filter(
        is_read=False
    ).order_by('-created_date')[:5]
    
    # Calculate summary statistics
    total_insights = ActionableInsight.objects.filter(is_addressed=False).count()
    high_priority_insights = ActionableInsight.objects.filter(
        is_addressed=False, 
        priority_score__gte=80
    ).count()
    total_patients_impacted = sum(
        ActionableInsight.objects.filter(is_addressed=False).values_list('patient_impact', flat=True)
    )
    
    context = {
        'user_role': 'HCR',
        'overdue_hcps': overdue_hcps,
        'recent_research': recent_research,
        'recent_emr_data': recent_emr_data,
        'all_hcps': all_hcps,
        'actionable_insights': actionable_insights,
        'patient_cohorts': patient_cohorts,
        'cohort_recommendations': cohort_recommendations,
        'total_insights': total_insights,
        'high_priority_insights': high_priority_insights,
        'total_patients_impacted': total_patients_impacted,
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
def mark_insight_addressed(request, insight_id):
    """Mark an actionable insight as addressed"""
    insight = get_object_or_404(ActionableInsight, id=insight_id)
    insight.is_addressed = True
    insight.save()
    messages.success(request, 'Insight marked as addressed.')
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
