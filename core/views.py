from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from .models import (HCP, ResearchUpdate, EMRData, Engagement, UserProfile, HCRRecommendation, 
                    PatientCohort, TreatmentOutcome, CohortRecommendation, ActionableInsight,
                    AnonymizedPatient, EMRDataPoint, PatientOutcome, PatientCluster, 
                    ClusterMembership, ClusterInsight, DrugRecommendation)

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
    
    # Get drug recommendations
    drug_recommendations = DrugRecommendation.objects.filter(
        is_reviewed=False
    ).order_by('-priority', '-success_rate')[:10]
    
    # Get patient clusters
    patient_clusters = PatientCluster.objects.all()[:10]
    
    # Get cluster insights
    cluster_insights = ClusterInsight.objects.filter(
        is_implemented=False
    ).order_by('-confidence_score')[:10]
    
    # Calculate summary statistics
    total_insights = ActionableInsight.objects.filter(is_addressed=False).count()
    high_priority_insights = ActionableInsight.objects.filter(
        is_addressed=False, 
        priority_score__gte=80
    ).count()
    total_patients_impacted = sum(
        ActionableInsight.objects.filter(is_addressed=False).values_list('patient_impact', flat=True)
    )
    
    # Get total patient count
    total_patients = AnonymizedPatient.objects.count()
    
    context = {
        'user_role': 'HCR',
        'overdue_hcps': overdue_hcps,
        'recent_research': recent_research,
        'recent_emr_data': recent_emr_data,
        'all_hcps': all_hcps,
        'actionable_insights': actionable_insights,
        'patient_cohorts': patient_cohorts,
        'cohort_recommendations': cohort_recommendations,
        'drug_recommendations': drug_recommendations,
        'patient_clusters': patient_clusters,
        'cluster_insights': cluster_insights,
        'total_insights': total_insights,
        'high_priority_insights': high_priority_insights,
        'total_patients_impacted': total_patients_impacted,
        'total_patients': total_patients,
    }
    return render(request, 'core/hcr_dashboard.html', context)

def hcp_dashboard(request, user_profile):
    """Dashboard for Healthcare Providers"""
    # Get the HCP associated with this user
    try:
        hcp = HCP.objects.get(user=request.user)
    except HCP.DoesNotExist:
        hcp = None
    
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
    
    # Get HCP's patients
    patients = []
    patient_clusters = []
    drug_recommendations = []
    
    if hcp:
        patients = AnonymizedPatient.objects.filter(hcp=hcp).order_by('-last_visit_date')[:50]
        patient_clusters = PatientCluster.objects.filter(hcp=hcp)
        drug_recommendations = DrugRecommendation.objects.filter(hcp=hcp, is_reviewed=False)
    
    context = {
        'user_role': 'HCP',
        'user_profile': user_profile,
        'recommendations': recommendations,
        'specialty_research': specialty_research,
        'general_research': general_research,
        'unread_count': unread_count,
        'patients': patients,
        'patient_clusters': patient_clusters,
        'drug_recommendations': drug_recommendations,
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
def mark_recommendation_reviewed(request, recommendation_id):
    """Mark a drug recommendation as reviewed"""
    recommendation = get_object_or_404(DrugRecommendation, id=recommendation_id)
    recommendation.is_reviewed = True
    recommendation.save()
    messages.success(request, 'Drug recommendation marked as reviewed.')
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
    
    # Get patient data for this HCP
    patients = AnonymizedPatient.objects.filter(hcp=hcp).order_by('-last_visit_date')[:50]
    patient_clusters = PatientCluster.objects.filter(hcp=hcp)
    drug_recommendations = DrugRecommendation.objects.filter(hcp=hcp, is_reviewed=False)
    
    context = {
        'hcp': hcp,
        'engagements': engagements,
        'emr_data': emr_data,
        'relevant_research': relevant_research,
        'patients': patients,
        'patient_clusters': patient_clusters,
        'drug_recommendations': drug_recommendations,
    }
    return render(request, 'core/hcp_profile.html', context)

@login_required
def patient_database(request):
    """View all patients across all HCPs for HCRs, or HCP's own patients for HCPs"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Get filter parameters
    specialty_filter = request.GET.get('specialty', '')
    diagnosis_filter = request.GET.get('diagnosis', '')
    hcp_filter = request.GET.get('hcp', '')
    
    if user_profile.role == 'HCP':
        # HCPs see only their own patients
        patients = AnonymizedPatient.objects.filter(hcp__user=request.user).select_related('hcp')
        page_title = "My Patients"
        show_hcp_column = False
    else:
        # HCRs see all patients
        patients = AnonymizedPatient.objects.select_related('hcp').all()
        page_title = "All Patients"
        show_hcp_column = True
    
    # Apply filters
    if specialty_filter:
        patients = patients.filter(hcp__specialty__icontains=specialty_filter)
    if diagnosis_filter:
        patients = patients.filter(primary_diagnosis__icontains=diagnosis_filter)
    if hcp_filter and user_profile.role == 'HCR':
        patients = patients.filter(hcp__name__icontains=hcp_filter)
    
    patients = patients.order_by('-last_visit_date')[:200]  # Increased limit to show more patients
    
    # Get filter options
    specialties = HCP.objects.values_list('specialty', flat=True).distinct()
    diagnoses = AnonymizedPatient.objects.values_list('primary_diagnosis', flat=True).distinct()
    hcps = HCP.objects.all()
    
    context = {
        'patients': patients,
        'specialties': specialties,
        'diagnoses': diagnoses,
        'hcps': hcps,
        'current_specialty': specialty_filter,
        'current_diagnosis': diagnosis_filter,
        'current_hcp': hcp_filter,
        'page_title': page_title,
        'show_hcp_column': show_hcp_column,
        'user_role': user_profile.role,
    }
    return render(request, 'core/patient_database.html', context)

@login_required
def patient_detail(request, patient_id):
    """View detailed patient information"""
    patient = get_object_or_404(AnonymizedPatient, patient_id=patient_id)
    
    # Get patient's EMR data points
    emr_data_points = EMRDataPoint.objects.filter(patient=patient).order_by('-date_recorded')
    
    # Get patient outcomes
    outcomes = PatientOutcome.objects.filter(patient=patient).order_by('-outcome_date')
    
    # Get cluster memberships
    cluster_memberships = ClusterMembership.objects.filter(patient=patient).select_related('cluster')
    
    context = {
        'patient': patient,
        'emr_data_points': emr_data_points,
        'outcomes': outcomes,
        'cluster_memberships': cluster_memberships,
    }
    return render(request, 'core/patient_detail.html', context)

@login_required
def cluster_detail(request, cluster_id):
    """View detailed cluster information"""
    cluster = get_object_or_404(PatientCluster, id=cluster_id)
    
    # Get cluster members
    cluster_members = ClusterMembership.objects.filter(cluster=cluster).select_related('patient')
    
    # Get cluster insights
    insights = ClusterInsight.objects.filter(cluster=cluster).order_by('-confidence_score')
    
    # Get drug recommendations for this cluster
    drug_recommendations = DrugRecommendation.objects.filter(cluster=cluster)
    
    context = {
        'cluster': cluster,
        'cluster_members': cluster_members,
        'insights': insights,
        'drug_recommendations': drug_recommendations,
    }
    return render(request, 'core/cluster_detail.html', context)

@login_required
def add_patient(request):
    """Add a new patient to HCP's database"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    if user_profile.role != 'HCP':
        messages.error(request, 'Only HCPs can add patients.')
        return redirect('dashboard')
    
    # Get the HCP associated with this user
    try:
        hcp = HCP.objects.get(user=request.user)
    except HCP.DoesNotExist:
        messages.error(request, 'HCP profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Generate a unique patient ID
        import random
        patient_id = f"P{random.randint(100000, 999999)}"
        while AnonymizedPatient.objects.filter(patient_id=patient_id).exists():
            patient_id = f"P{random.randint(100000, 999999)}"
        
        # Create the patient
        patient = AnonymizedPatient.objects.create(
            patient_id=patient_id,
            hcp=hcp,
            age_group=request.POST.get('age_group'),
            gender=request.POST.get('gender'),
            race=request.POST.get('race'),
            ethnicity=request.POST.get('ethnicity'),
            zip_code_prefix=request.POST.get('zip_code_prefix'),
            primary_diagnosis=request.POST.get('primary_diagnosis'),
            secondary_diagnoses=request.POST.get('secondary_diagnoses', ''),
            comorbidities=request.POST.get('comorbidities', ''),
            current_treatments=request.POST.get('current_treatments', ''),
            treatment_history=request.POST.get('treatment_history', ''),
            medication_adherence=request.POST.get('medication_adherence', 'Good'),
            last_lab_values={},
            vital_signs={},
            last_visit_date=request.POST.get('last_visit_date'),
            visit_frequency=request.POST.get('visit_frequency', 'Monthly'),
            emergency_visits_6m=int(request.POST.get('emergency_visits_6m', 0)),
            hospitalizations_6m=int(request.POST.get('hospitalizations_6m', 0)),
            risk_factors=request.POST.get('risk_factors', ''),
            family_history=request.POST.get('family_history', ''),
            insurance_type=request.POST.get('insurance_type', ''),
            medication_access=request.POST.get('medication_access', 'Good')
        )
        
        messages.success(request, f'Patient {patient_id} added successfully!')
        return redirect('patient_detail', patient_id=patient_id)
    
    context = {
        'hcp': hcp,
        'age_groups': ['18-25', '26-35', '36-45', '46-55', '56-65', '66-75', '76+'],
        'genders': [('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('U', 'Unknown')],
        'races': [('WHITE', 'White'), ('BLACK', 'Black or African American'), ('ASIAN', 'Asian'), 
                 ('NATIVE', 'American Indian or Alaska Native'), ('PACIFIC', 'Native Hawaiian or Other Pacific Islander'), 
                 ('OTHER', 'Other'), ('UNKNOWN', 'Unknown')],
        'ethnicities': [('HISPANIC', 'Hispanic or Latino'), ('NON_HISPANIC', 'Not Hispanic or Latino'), ('UNKNOWN', 'Unknown')],
        'visit_frequencies': ['Weekly', 'Monthly', 'Quarterly', 'As needed'],
        'medication_adherences': ['Excellent', 'Good', 'Fair', 'Poor'],
        'insurance_types': ['Private', 'Medicare', 'Medicaid', 'Uninsured'],
        'medication_accesses': ['Excellent', 'Good', 'Limited', 'Poor']
    }
    return render(request, 'core/add_patient.html', context)
