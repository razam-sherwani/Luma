from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg
from django.db import models
from django.utils import timezone
from datetime import date, timedelta
import json
import csv
from collections import Counter
from .models import (HCP, ResearchUpdate, EMRData, Engagement, UserProfile, HCRRecommendation, 
                    PatientCohort, TreatmentOutcome, CohortRecommendation, ActionableInsight,
                    AnonymizedPatient, PatientCluster, ClusterMembership, PatientOutcome, 
                    EMRDataPoint, ClusterInsight, DrugRecommendation, PatientIssueAnalysis,
                    ScrapedResearch, IntelligentRecommendation, HCRMessage, RecommendationFeedback)
from .research_generator import SimplifiedResearchGenerator

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
    
    # Get recent high-impact research updates
    recent_research = ResearchUpdate.objects.filter(is_high_impact=True).order_by('-relevance_score', '-date')[:5]
    
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
    
    # Get patient clusters for overview
    patient_clusters = PatientCluster.objects.all()[:6]
    
    # Get cluster insights
    cluster_insights = ClusterInsight.objects.all()[:4]
    
    # Get cohort recommendations
    cohort_recommendations = CohortRecommendation.objects.filter(
        is_read=False
    ).order_by('-created_date')[:5]
    
    # Get AI-powered drug recommendations based on cluster analysis
    drug_recommendations = DrugRecommendation.objects.select_related('hcp', 'cluster').order_by(
        '-priority', '-success_rate', '-created_date'
    )[:12]  # Show top 12 recommendations
    
    # Get recent intelligent recommendations created by this HCR
    recent_recommendations = IntelligentRecommendation.objects.filter(
        hcr_sender=request.user
    ).order_by('-created_date')[:5]
    
    # Generate dynamic recommendations based on cluster similarity
    dynamic_recommendations = generate_dynamic_drug_recommendations()
    
    # Calculate summary statistics
    total_insights = ActionableInsight.objects.filter(is_addressed=False).count()
    high_priority_insights = ActionableInsight.objects.filter(
        is_addressed=False, 
        priority_score__gte=80
    ).count()
    total_patients_impacted = sum(
        ActionableInsight.objects.filter(is_addressed=False).values_list('patient_impact', flat=True)
    )
    
    # Get actual patient statistics
    total_patients = AnonymizedPatient.objects.count()
    total_cohorts = PatientCohort.objects.count()
    total_clusters = PatientCluster.objects.count()
    
    context = {
        'user_role': 'HCR',
        'overdue_hcps': overdue_hcps,
        'recent_research': recent_research,
        'recent_emr_data': recent_emr_data,
        'all_hcps': all_hcps,
        'actionable_insights': actionable_insights,
        'patient_cohorts': patient_cohorts,
        'patient_clusters': patient_clusters,
        'cluster_insights': cluster_insights,
        'cohort_recommendations': cohort_recommendations,
        'drug_recommendations': drug_recommendations,
        'dynamic_recommendations': dynamic_recommendations,
        'total_insights': total_insights,
        'high_priority_insights': high_priority_insights,
        'total_patients_impacted': total_patients_impacted,
        'total_patients': total_patients,
        'total_cohorts': total_cohorts,
        'total_clusters': total_clusters,
        'recent_recommendations': recent_recommendations,
    }
    return render(request, 'core/hcr_dashboard_beautiful.html', context)

def hcp_dashboard(request, user_profile):
    """Dashboard for Healthcare Providers"""
    # Get HCP profile
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
    
    # Get personalized research using the enhanced generator
    research_generator = SimplifiedResearchGenerator()
    if user_profile.specialty:
        all_research = research_generator.get_personalized_research(user_profile.specialty, 8)
        # Split into specialty and general research for display
        specialty_research = [r for r in all_research if r.specialty == user_profile.specialty][:5]
        general_research = [r for r in all_research if r.specialty != user_profile.specialty][:3]
    else:
        # Fallback for users without specialty
        specialty_research = ResearchUpdate.objects.filter(is_high_impact=True).order_by('-relevance_score', '-date')[:5]
        general_research = ResearchUpdate.objects.exclude(id__in=[r.id for r in specialty_research]).order_by('-relevance_score', '-date')[:3]
    
    # Get patient statistics for this HCP
    patient_stats = {}
    if hcp:
        patients = AnonymizedPatient.objects.filter(hcp=hcp)
        patient_stats = {
            'total_patients': patients.count(),
            'recent_patients': patients.filter(last_visit_date__gte=date.today() - timedelta(days=30)).count(),
            'high_risk_patients': patients.filter(emergency_visits_6m__gte=2).count(),
            'common_diagnosis': patients.values('primary_diagnosis').annotate(
                count=models.Count('primary_diagnosis')
            ).order_by('-count').first()
        }
    
    context = {
        'user_role': 'HCP',
        'user_profile': user_profile,
        'hcp': hcp,
        'recommendations': recommendations,
        'specialty_research': specialty_research,
        'general_research': general_research,
        'unread_count': unread_count,
        'patient_stats': patient_stats,
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
    # This would typically work with DrugRecommendation model
    # For now, we'll just redirect back to dashboard
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
    
    context = {
        'hcp': hcp,
        'engagements': engagements,
        'emr_data': emr_data,
        'relevant_research': relevant_research,
    }
    return render(request, 'core/hcp_profile.html', context)

@login_required
def patient_database(request):
    """Display all patients in a database view"""
    # Get filter and search parameters
    current_specialty = request.GET.get('specialty', '')
    current_diagnosis = request.GET.get('diagnosis', '')
    current_hcp = request.GET.get('hcp', '')
    search_query = request.GET.get('search', '').strip()
    
    # Get user profile to determine role
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'HCR'}
    )
    
    # Get all patients
    patients = AnonymizedPatient.objects.select_related('hcp').all()
    
    # If user is an HCP, only show their patients
    if user_profile.role == 'HCP':
        try:
            hcp = HCP.objects.get(user=request.user)
            patients = patients.filter(hcp=hcp)
        except HCP.DoesNotExist:
            # If HCP profile doesn't exist, show no patients
            patients = AnonymizedPatient.objects.none()
    
    # Apply search filter first (most important)
    if search_query:
        patients = patients.filter(
            Q(patient_id__icontains=search_query) |
            Q(primary_diagnosis__icontains=search_query) |
            Q(secondary_diagnoses__icontains=search_query) |
            Q(comorbidities__icontains=search_query) |
            Q(current_treatments__icontains=search_query) |
            Q(treatment_history__icontains=search_query) |
            Q(risk_factors__icontains=search_query) |
            Q(family_history__icontains=search_query) |
            Q(hcp__name__icontains=search_query) |
            Q(hcp__specialty__icontains=search_query) |
            Q(age_group__icontains=search_query) |
            Q(gender__icontains=search_query) |
            Q(race__icontains=search_query) |
            Q(ethnicity__icontains=search_query) |
            Q(zip_code_prefix__icontains=search_query) |
            Q(insurance_type__icontains=search_query) |
            Q(medication_adherence__icontains=search_query)
        )

    # Apply additional filters
    if current_specialty:
        patients = patients.filter(hcp__specialty=current_specialty)
    if current_diagnosis:
        patients = patients.filter(primary_diagnosis__icontains=current_diagnosis)
    if current_hcp:
        patients = patients.filter(hcp__name__icontains=current_hcp)
    
    # Get unique values for filter dropdowns (from all accessible patients, not filtered)
    all_patients = AnonymizedPatient.objects.select_related('hcp').all()
    if user_profile.role == 'HCP':
        try:
            hcp = HCP.objects.get(user=request.user)
            all_patients = all_patients.filter(hcp=hcp)
        except HCP.DoesNotExist:
            all_patients = AnonymizedPatient.objects.none()

    specialties = list(set(all_patients.values_list('hcp__specialty', flat=True)))
    specialties = [s for s in specialties if s]
    
    diagnoses = list(set(all_patients.values_list('primary_diagnosis', flat=True)))
    diagnoses = [d for d in diagnoses if d]
    
    hcps = HCP.objects.all() if user_profile.role == 'HCR' else []

    # Order patients by most recent visit
    patients = patients.order_by('-last_visit_date', 'patient_id')
    
    context = {
        'patients': patients,
        'specialties': specialties,
        'diagnoses': diagnoses,
        'hcps': hcps,
        'current_specialty': current_specialty,
        'current_diagnosis': current_diagnosis,
        'current_hcp': current_hcp,
        'search_query': search_query,
        'show_hcp_column': user_profile.role == 'HCR',
        'user_role': user_profile.role,
        'page_title': 'Patient Database'
    }
    return render(request, 'core/patient_database.html', context)

@login_required
def patient_detail(request, patient_id):
    """Display detailed information about a specific patient"""
    try:
        patient = AnonymizedPatient.objects.select_related('hcp').get(patient_id=patient_id)
        
        # Get user profile to check permissions
        user_profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'role': 'HCR'}
        )
        
        # If user is HCP, check if they can view this patient
        if user_profile.role == 'HCP':
            try:
                hcp = HCP.objects.get(user=request.user)
                if patient.hcp != hcp:
                    from django.http import Http404
                    raise Http404("Patient not found")
            except HCP.DoesNotExist:
                from django.http import Http404
                raise Http404("Patient not found")
        
        # Get related data
        emr_data = patient.data_points.all().order_by('-date_recorded')[:10]  # Last 10 records
        outcomes = patient.outcomes.all().order_by('-outcome_date')[:5]   # Last 5 outcomes
        cluster_memberships = patient.cluster_memberships.all().select_related('cluster')[:5]  # Up to 5 clusters
        
        context = {
            'patient': patient,
            'emr_data': emr_data,
            'outcomes': outcomes,
            'cluster_memberships': cluster_memberships,
            'user_role': user_profile.role,
        }
        return render(request, 'core/patient_detail.html', context)
        
    except AnonymizedPatient.DoesNotExist:
        from django.http import Http404
        raise Http404("Patient not found")

@login_required
def cluster_detail(request, cluster_id):
    """Display detailed information about a specific cluster"""
    # This would show detailed cluster information
    # For now, return a simple response
    context = {
        'cluster_id': cluster_id,
    }
    return render(request, 'core/cluster_detail.html', context)

@login_required
def add_patient(request):
    """Add a new patient to the system - HCPs only"""
    # Check if user is an HCP
    if request.user.userprofile.role != 'HCP':
        messages.error(request, 'Only Healthcare Providers can add patients.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            # Get the HCP profile
            hcp = HCP.objects.get(user=request.user)

            # Generate a unique patient ID
            import uuid
            patient_id = f"PAT_{uuid.uuid4().hex[:8].upper()}"

            # Create the patient record
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
                medication_adherence=request.POST.get('medication_adherence', ''),
                last_visit_date=request.POST.get('last_visit_date'),
                visit_frequency=request.POST.get('visit_frequency', ''),
                emergency_visits_6m=int(request.POST.get('emergency_visits_6m', 0)),
                hospitalizations_6m=int(request.POST.get('hospitalizations_6m', 0)),
                risk_factors=request.POST.get('risk_factors', ''),
                family_history=request.POST.get('family_history', ''),
                insurance_type=request.POST.get('insurance_type', ''),
                medication_access=request.POST.get('medication_access', ''),
            )

            messages.success(request, f'Patient {patient.patient_id} added successfully!')
            return redirect('patient_database')
    
        except HCP.DoesNotExist:
            messages.error(request, 'HCP profile not found. Please contact support.')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error adding patient: {str(e)}')

    # Prepare form choices
    age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '66-75', '76+']
    genders = AnonymizedPatient.GENDER_CHOICES
    races = AnonymizedPatient.RACE_CHOICES
    ethnicities = AnonymizedPatient.ETHNICITY_CHOICES
    medication_adherences = ['Excellent', 'Good', 'Fair', 'Poor', 'Unknown']
    visit_frequencies = ['Weekly', 'Monthly', 'Quarterly', 'Semi-annually', 'Annually', 'As needed']
    insurance_types = ['Medicare', 'Medicaid', 'Private', 'Self-pay', 'Other']
    medication_accesses = ['Excellent', 'Good', 'Limited', 'Poor']

    context = {
        'age_groups': age_groups,
        'genders': genders,
        'races': races,
        'ethnicities': ethnicities,
        'medication_adherences': medication_adherences,
        'visit_frequencies': visit_frequencies,
        'insurance_types': insurance_types,
        'medication_accesses': medication_accesses,
    }
    return render(request, 'core/add_patient.html', context)

@login_required
def cohort_cluster_network(request):
    """Interactive network visualization showing treatment similarities between clusters"""
    
    # Get filter parameters
    current_specialty = request.GET.get('specialty', '')
    current_treatment = request.GET.get('treatment', '')
    current_diagnosis = request.GET.get('diagnosis', '')
    current_risk = request.GET.get('risk', '')
    
    # Get clusters (simplified to avoid SQLite expression tree error)
    clusters = PatientCluster.objects.select_related('hcp')
    
    # Apply specialty filter first, then slice
    if current_specialty:
        clusters = clusters.filter(hcp__specialty=current_specialty)
    
    # Limit to 20 clusters for performance
    clusters = clusters[:20]
    
    # Get unique values for filter dropdowns from ALL data (not just filtered clusters)
    specialties = list(set(PatientCluster.objects.values_list('hcp__specialty', flat=True)))
    specialties = [s for s in specialties if s]  # Remove None values
    
    # Get unique treatments and diagnoses from ALL patients
    all_treatments = set()
    all_diagnoses = set()
    
    # Get treatments from all outcomes
    for outcome in PatientOutcome.objects.all()[:500]:  # Sample 500 outcomes
        if outcome.treatment:
            all_treatments.add(outcome.treatment)
    
    # Get diagnoses from all patients
    for patient in AnonymizedPatient.objects.all()[:1000]:  # Sample 1000 patients
            if patient.primary_diagnosis:
                all_diagnoses.add(patient.primary_diagnosis)
    
    treatments = sorted(list(all_treatments))
    diagnoses = sorted(list(all_diagnoses))
    
    # Build nodes data - each cluster is a node
    nodes = []
    cluster_treatments = {}  # Store treatments for each cluster
    
    for cluster in clusters:
        # Get all treatments used in this cluster
        cluster_treatment_list = []
        cluster_diagnoses = set()
        
        # Limit to first 15 patients per cluster for better connections
        for membership in cluster.patients.all()[:15]:
            patient = membership.patient
            for outcome in patient.outcomes.all()[:3]:  # 3 outcomes per patient
                cluster_treatment_list.append(outcome.treatment)
            if patient.primary_diagnosis:
                cluster_diagnoses.add(patient.primary_diagnosis)
        
        # Apply treatment filter
        if current_treatment and current_treatment not in cluster_treatment_list:
            continue
            
        # Apply diagnosis filter
        if current_diagnosis and current_diagnosis not in cluster_diagnoses:
            continue
        
        # Calculate cluster metrics
        treatment_counts = {}
        for treatment in cluster_treatment_list:
            treatment_counts[treatment] = treatment_counts.get(treatment, 0) + 1
        
        # Get most common treatments
        common_treatments = sorted(treatment_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        common_treatment_names = [t[0] for t in common_treatments]
        
        # Calculate success rate (simplified)
        success_rate = 75.0 + (cluster.patient_count * 0.5)  # Mock calculation
        
        # Apply risk filter (simplified - based on patient count)
        if current_risk:
            if current_risk == 'high' and cluster.patient_count <= 40:
                continue
            elif current_risk == 'medium' and (cluster.patient_count <= 20 or cluster.patient_count > 40):
                continue
            elif current_risk == 'low' and cluster.patient_count > 20:
                continue
        
        # Store treatments for similarity calculation
        cluster_treatments[cluster.id] = set(cluster_treatment_list)
        
        nodes.append({
            'id': f"cluster_{cluster.id}",
            'name': cluster.name,
            'type': 'cluster',
            'patient_count': cluster.patient_count,
            'success_rate': round(success_rate, 1),
            'specialty': cluster.hcp.specialty if cluster.hcp else 'Unknown',
            'diagnoses': list(cluster_diagnoses),
            'treatments': cluster_treatment_list,
            'common_treatments': common_treatment_names,
            'treatment_counts': treatment_counts,
            'description': cluster.description or f"AI-discovered cluster with {cluster.patient_count} patients"
        })
    
    # Calculate treatment similarity between clusters
    links = []
    cluster_ids = list(cluster_treatments.keys())
    cluster_connection_counts = {cid: 0 for cid in cluster_ids}  # Track connections per cluster
    max_connections_per_cluster = 5  # Limit connections to make it more realistic
    
    for i, cluster1_id in enumerate(cluster_ids):
        for cluster2_id in cluster_ids[i+1:]:
            treatments1 = cluster_treatments[cluster1_id]
            treatments2 = cluster_treatments[cluster2_id]
            
            # Get comprehensive patient data for both clusters
            cluster1_data = {'patients': [], 'demographics': {}, 'outcomes': [], 'comorbidities': set()}
            cluster2_data = {'patients': [], 'demographics': {}, 'outcomes': [], 'comorbidities': set()}
            
            # Collect detailed patient data for each cluster
            for cluster in clusters:
                if cluster.id == cluster1_id:
                    for membership in cluster.patients.all()[:15]:
                        patient = membership.patient
                        cluster1_data['patients'].append(patient)
                        # Demographics
                        if patient.age_group not in cluster1_data['demographics']:
                            cluster1_data['demographics'][patient.age_group] = 0
                        cluster1_data['demographics'][patient.age_group] += 1
                        # Comorbidities
                        if patient.comorbidities:
                            cluster1_data['comorbidities'].update(patient.comorbidities.split(','))
                        # Outcomes
                        for outcome in patient.outcomes.all()[:3]:
                            cluster1_data['outcomes'].append(outcome)
                            
                elif cluster.id == cluster2_id:
                    for membership in cluster.patients.all()[:15]:
                        patient = membership.patient
                        cluster2_data['patients'].append(patient)
                        # Demographics
                        if patient.age_group not in cluster2_data['demographics']:
                            cluster2_data['demographics'][patient.age_group] = 0
                        cluster2_data['demographics'][patient.age_group] += 1
                        # Comorbidities
                        if patient.comorbidities:
                            cluster2_data['comorbidities'].update(patient.comorbidities.split(','))
                        # Outcomes
                        for outcome in patient.outcomes.all()[:3]:
                            cluster2_data['outcomes'].append(outcome)
            
            # 1. Treatment Similarity (25% weight)
            intersection = len(treatments1.intersection(treatments2))
            union = len(treatments1.union(treatments2))
            treatment_similarity = intersection / union if union > 0 else 0
            
            # 2. Diagnosis Similarity (20% weight)
            cluster1_diagnoses = set()
            cluster2_diagnoses = set()
            for patient in cluster1_data['patients']:
                if patient.primary_diagnosis:
                    cluster1_diagnoses.add(patient.primary_diagnosis)
            for patient in cluster2_data['patients']:
                if patient.primary_diagnosis:
                    cluster2_diagnoses.add(patient.primary_diagnosis)
            
            diag_intersection = len(cluster1_diagnoses.intersection(cluster2_diagnoses))
            diag_union = len(cluster1_diagnoses.union(cluster2_diagnoses))
            diagnosis_similarity = diag_intersection / diag_union if diag_union > 0 else 0
            
            # 3. Demographic Similarity (20% weight) - Age group overlap
            age1 = set(cluster1_data['demographics'].keys())
            age2 = set(cluster2_data['demographics'].keys())
            age_intersection = len(age1.intersection(age2))
            age_union = len(age1.union(age2))
            demographic_similarity = age_intersection / age_union if age_union > 0 else 0
            
            # 4. Comorbidity Similarity (15% weight) - Shared conditions
            comorbidity_intersection = len(cluster1_data['comorbidities'].intersection(cluster2_data['comorbidities']))
            comorbidity_union = len(cluster1_data['comorbidities'].union(cluster2_data['comorbidities']))
            comorbidity_similarity = comorbidity_intersection / comorbidity_union if comorbidity_union > 0 else 0
            
            # 5. Geographic Similarity (10% weight) - Zip code proximity
            zip1 = set(p.zip_code_prefix for p in cluster1_data['patients'] if p.zip_code_prefix)
            zip2 = set(p.zip_code_prefix for p in cluster2_data['patients'] if p.zip_code_prefix)
            zip_intersection = len(zip1.intersection(zip2))
            zip_union = len(zip1.union(zip2))
            geographic_similarity = zip_intersection / zip_union if zip_union > 0 else 0
            
            # 6. Clinical Outcome Similarity (10% weight) - Treatment success patterns
            outcome_similarity = 0
            if cluster1_data['outcomes'] and cluster2_data['outcomes']:
                # Calculate average success rates (simplified)
                success1 = sum(1 for o in cluster1_data['outcomes'] if 'success' in o.treatment.lower() or 'effective' in o.treatment.lower()) / len(cluster1_data['outcomes'])
                success2 = sum(1 for o in cluster2_data['outcomes'] if 'success' in o.treatment.lower() or 'effective' in o.treatment.lower()) / len(cluster2_data['outcomes'])
                outcome_similarity = 1 - abs(success1 - success2)  # Closer success rates = higher similarity
            
            # Weighted combined similarity for clinically meaningful connections
            combined_similarity = (
                treatment_similarity * 0.25 +
                diagnosis_similarity * 0.20 +
                demographic_similarity * 0.20 +
                comorbidity_similarity * 0.15 +
                geographic_similarity * 0.10 +
                outcome_similarity * 0.10
            )
            
            # Create links only for clusters with significant medical relevance
            # Must meet at least 2 of these criteria for a meaningful connection:
            meaningful_connections = 0
            if treatment_similarity > 0.3:
                meaningful_connections += 1
            if diagnosis_similarity > 0.3:
                meaningful_connections += 1
            if demographic_similarity > 0.4:
                meaningful_connections += 1
            if comorbidity_similarity > 0.2:
                meaningful_connections += 1
            if geographic_similarity > 0.3:
                meaningful_connections += 1
            
            # Only connect if: high overall similarity OR multiple meaningful factors
            # Add some randomness to break perfect symmetry and make it look more natural
            import random
            random_factor = random.uniform(0.95, 1.05)  # ±5% variation
            adjusted_similarity = combined_similarity * random_factor
            
            # Check if both clusters haven't exceeded their connection limit
            if (adjusted_similarity > 0.4 or (adjusted_similarity > 0.25 and meaningful_connections >= 2)) and \
               cluster_connection_counts[cluster1_id] < max_connections_per_cluster and \
               cluster_connection_counts[cluster2_id] < max_connections_per_cluster:
                # Determine link strength and color based on combined similarity
                if combined_similarity > 0.5:
                    link_strength = 'strong'
                    link_color = '#e74c3c'  # Red for high similarity
                elif combined_similarity > 0.3:
                    link_strength = 'medium'
                    link_color = '#f39c12'  # Orange for medium similarity
                else:
                    link_strength = 'weak'
                    link_color = '#27ae60'  # Green for low similarity
                
                # Generate meaningful connection description
                connection_reasons = []
                if treatment_similarity > 0.3:
                    connection_reasons.append(f"Shared treatments ({len(treatments1.intersection(treatments2))} common)")
                if diagnosis_similarity > 0.3:
                    connection_reasons.append(f"Similar diagnoses ({len(cluster1_diagnoses.intersection(cluster2_diagnoses))} common)")
                if demographic_similarity > 0.3:
                    connection_reasons.append(f"Similar age groups ({len(age1.intersection(age2))} common)")
                if comorbidity_similarity > 0.2:
                    connection_reasons.append(f"Shared comorbidities ({len(cluster1_data['comorbidities'].intersection(cluster2_data['comorbidities']))} common)")
                if geographic_similarity > 0.2:
                    connection_reasons.append(f"Geographic proximity ({len(zip1.intersection(zip2))} common zip codes)")
                
                connection_description = "; ".join(connection_reasons) if connection_reasons else "Low-level similarity"
                
                links.append({
                    'source': f"cluster_{cluster1_id}",
                    'target': f"cluster_{cluster2_id}",
                    'similarity': round(combined_similarity * 100, 1),
                    'strength': link_strength,
                    'color': link_color,
                    'shared_treatments': list(treatments1.intersection(treatments2)),
                    'shared_diagnoses': list(cluster1_diagnoses.intersection(cluster2_diagnoses)),
                    'shared_comorbidities': list(cluster1_data['comorbidities'].intersection(cluster2_data['comorbidities'])),
                    'shared_age_groups': list(age1.intersection(age2)),
                    'shared_zip_codes': list(zip1.intersection(zip2)),
                    'connection_reasons': connection_description,
                    'treatment_similarity': round(treatment_similarity * 100, 1),
                    'diagnosis_similarity': round(diagnosis_similarity * 100, 1),
                    'demographic_similarity': round(demographic_similarity * 100, 1),
                    'comorbidity_similarity': round(comorbidity_similarity * 100, 1),
                    'geographic_similarity': round(geographic_similarity * 100, 1),
                    'outcome_similarity': round(outcome_similarity * 100, 1)
                })
                
                # Update connection counts
                cluster_connection_counts[cluster1_id] += 1
                cluster_connection_counts[cluster2_id] += 1
    
    context = {
        'nodes': json.dumps(nodes),
        'links': json.dumps(links),
        'specialties': specialties,
        'treatments': treatments,
        'diagnoses': diagnoses,
        'current_specialty': current_specialty,
        'current_treatment': current_treatment,
        'current_diagnosis': current_diagnosis,
        'current_risk': current_risk,
    }
    
    return render(request, 'core/cohort_cluster_network.html', context)

def calculate_patient_overlap(node1, node2):
    """Calculate percentage of overlapping patients between two nodes"""
    # Simulate patient overlap based on specialty and condition similarity
    base_overlap = 5  # Base 5% overlap
    
    # Increase overlap if same specialty
    if node1['specialty'] == node2['specialty']:
        base_overlap += 15
    
    # Increase overlap if similar conditions
    if node1['condition'] == node2['condition']:
        base_overlap += 25
    elif any(word in node2['condition'].lower() for word in node1['condition'].lower().split()):
        base_overlap += 10
    
    # Add some randomness for realism
    import random
    base_overlap += random.uniform(-5, 10)
    
    return max(0, min(100, base_overlap))

def calculate_treatment_similarity(node1, node2):
    """Calculate treatment pattern similarity between two nodes"""
    # Simulate treatment similarity based on condition and specialty
    base_similarity = 20  # Base 20% similarity
    
    # Increase similarity if same specialty
    if node1['specialty'] == node2['specialty']:
        base_similarity += 30
    
    # Increase similarity if similar conditions
    if node1['condition'] == node2['condition']:
        base_similarity += 40
    elif any(word in node2['condition'].lower() for word in node1['condition'].lower().split()):
        base_similarity += 20
    
    # Add some randomness
    import random
    base_similarity += random.uniform(-10, 15)
    
    return max(0, min(100, base_similarity))

def calculate_patient_similarity(node1, node2):
    """Calculate patient count similarity between two nodes"""
    count1 = node1.get('patient_count', 0)
    count2 = node2.get('patient_count', 0)
    
    if count1 == 0 and count2 == 0:
        return 0
    
    # Calculate similarity based on patient count difference
    max_count = max(count1, count2)
    min_count = min(count1, count2)
    similarity = (min_count / max_count) * 100 if max_count > 0 else 0
    
    return similarity

def generate_intervention_recommendation(node1, node2, similarity):
    """Generate recommended intervention based on node similarity"""
    if similarity > 0.7:
        return f"High similarity detected - consider unified treatment protocols for both {node1['name']} and {node2['name']}"
    elif similarity > 0.5:
        return f"Moderate similarity - evaluate cross-cohort treatment strategies between {node1['name']} and {node2['name']}"
    else:
        return f"Low similarity - monitor for potential treatment pattern convergence between {node1['name']} and {node2['name']}"

def generate_dynamic_drug_recommendations():
    """Generate dynamic drug recommendations based on cluster similarity analysis"""
    from datetime import datetime, timedelta
    import random
    
    recommendations = []
    
    # Get clusters with their similarity data
    clusters = PatientCluster.objects.select_related('hcp').prefetch_related('patients__patient__outcomes')[:20]
    
    # Get all treatments and their success rates
    all_treatments = {}
    for cluster in clusters:
        for membership in cluster.patients.all()[:10]:
            for outcome in membership.patient.outcomes.all()[:3]:
                treatment = outcome.treatment
                if treatment not in all_treatments:
                    all_treatments[treatment] = {'success_count': 0, 'total_count': 0, 'clusters': set()}
                
                all_treatments[treatment]['total_count'] += 1
                all_treatments[treatment]['clusters'].add(cluster.id)
                
                # Simple success detection based on treatment name
                if any(keyword in treatment.lower() for keyword in ['success', 'effective', 'improved', 'positive']):
                    all_treatments[treatment]['success_count'] += 1
    
    # Generate recommendations based on cluster similarity patterns
    for cluster in clusters:
        if cluster.patient_count < 5:  # Skip small clusters
            continue
            
        # Find similar clusters (simplified similarity check)
        similar_clusters = []
        for other_cluster in clusters:
            if other_cluster.id != cluster.id:
                # Check for treatment overlap
                cluster_treatments = set()
                other_treatments = set()
                
                for membership in cluster.patients.all()[:5]:
                    for outcome in membership.patient.outcomes.all()[:2]:
                        cluster_treatments.add(outcome.treatment)
                
                for membership in other_cluster.patients.all()[:5]:
                    for outcome in membership.patient.outcomes.all()[:2]:
                        other_treatments.add(outcome.treatment)
                
                overlap = len(cluster_treatments.intersection(other_treatments))
                if overlap > 0:
                    similarity = overlap / len(cluster_treatments.union(other_treatments))
                    if similarity > 0.3:  # 30% treatment overlap
                        similar_clusters.append((other_cluster, similarity))
        
        # Generate recommendations for this cluster
        for treatment, data in all_treatments.items():
            if cluster.id in data['clusters'] and data['total_count'] >= 3:
                success_rate = (data['success_count'] / data['total_count']) * 100
                
                # Calculate priority based on success rate and cluster similarity
                priority_score = success_rate
                if similar_clusters:
                    avg_similarity = sum(sim for _, sim in similar_clusters) / len(similar_clusters)
                    priority_score += avg_similarity * 20  # Boost for similarity
                
                # Determine priority level
                if priority_score >= 80:
                    priority = 'HIGH'
                elif priority_score >= 60:
                    priority = 'MEDIUM'
                else:
                    priority = 'LOW'
                
                # Generate evidence level
                if data['total_count'] >= 10 and success_rate >= 70:
                    evidence_level = 'High'
                elif data['total_count'] >= 5 and success_rate >= 50:
                    evidence_level = 'Moderate'
                else:
                    evidence_level = 'Low'
                
                # Create recommendation
                recommendation = {
                    'cluster_id': cluster.id,
                    'cluster_name': cluster.name,
                    'hcp': cluster.hcp,
                    'drug_name': treatment,
                    'indication': f"Based on {cluster.name} patient patterns",
                    'success_rate': round(success_rate, 1),
                    'patient_count': data['total_count'],
                    'evidence_level': evidence_level,
                    'priority': priority,
                    'priority_score': round(priority_score, 1),
                    'similar_clusters': len(similar_clusters),
                    'research_support': f"Evidence from {data['total_count']} patients across {len(data['clusters'])} clusters",
                    'contraindications': "Check patient history for allergies and comorbidities",
                    'side_effects': "Monitor for common adverse reactions",
                    'dosage_recommendations': "Start with standard dosing, adjust based on patient response",
                    'created_date': datetime.now().date(),
                    'is_dynamic': True,
                    'similarity_data': {
                        'treatment_overlap': len([c for c in similar_clusters if c[1] > 0.5]),
                        'avg_similarity': round(sum(sim for _, sim in similar_clusters) / len(similar_clusters) * 100, 1) if similar_clusters else 0
                    }
                }
                
                recommendations.append(recommendation)
    
    # Sort by priority score and return top recommendations
    recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
    return recommendations[:8]  # Return top 8 dynamic recommendations

def parse_emr_file(emr_file):
    """Parse EMR file and extract patient data"""
    try:
        # Read file content
        file_extension = emr_file.name.lower().split('.')[-1]

        if file_extension == 'csv':
            # Read CSV file
            df = pd.read_csv(io.StringIO(emr_file.read().decode('utf-8')))
        elif file_extension in ['xlsx', 'xls']:
            # Read Excel file
            df = pd.read_excel(emr_file)
        else:
            return None, "Unsupported file format. Please upload CSV or Excel files."

        # Define expected columns and their mappings
        column_mappings = {
            # Demographics
            'age': ['age', 'age_group', 'patient_age'],
            'gender': ['gender', 'sex', 'patient_gender'],
            'race': ['race', 'ethnicity', 'patient_race'],
            'zip_code': ['zip', 'zip_code', 'zipcode', 'postal_code'],

            # Medical
            'primary_diagnosis': ['diagnosis', 'primary_diagnosis', 'main_diagnosis', 'condition'],
            'secondary_diagnoses': ['secondary_diagnosis', 'secondary_diagnoses', 'other_diagnoses'],
            'comorbidities': ['comorbidities', 'comorbidity', 'other_conditions'],

            # Treatment
            'current_treatments': ['treatment', 'current_treatment', 'medications', 'current_medications'],
            'treatment_history': ['treatment_history', 'past_treatments', 'medication_history'],

            # Vital signs
            'last_visit_date': ['visit_date', 'last_visit', 'appointment_date', 'date'],
            'emergency_visits': ['emergency_visits', 'er_visits', 'emergency_room_visits'],
            'hospitalizations': ['hospitalizations', 'hospital_admissions', 'admissions'],

            # Additional
            'risk_factors': ['risk_factors', 'risks', 'patient_risks'],
            'family_history': ['family_history', 'family_medical_history'],
            'insurance': ['insurance', 'insurance_type', 'coverage'],
        }

        # Extract patient data
        patient_data = {}

        # Normalize column names
        df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]

        # Map columns to expected fields
        for field, possible_columns in column_mappings.items():
            for col in possible_columns:
                if col in df.columns:
                    patient_data[field] = df[col].iloc[0] if not df[col].empty else ''
                    break
            if field not in patient_data:
                patient_data[field] = ''

        # Process age group
        if 'age' in patient_data and patient_data['age']:
            try:
                age = int(patient_data['age'])
                if age < 26:
                    patient_data['age_group'] = '18-25'
                elif age < 36:
                    patient_data['age_group'] = '26-35'
                elif age < 46:
                    patient_data['age_group'] = '36-45'
                elif age < 56:
                    patient_data['age_group'] = '46-55'
                elif age < 66:
                    patient_data['age_group'] = '56-65'
                elif age < 76:
                    patient_data['age_group'] = '66-75'
                else:
                    patient_data['age_group'] = '76+'
            except (ValueError, TypeError):
                patient_data['age_group'] = '26-35'  # Default
        else:
            patient_data['age_group'] = '26-35'  # Default

        # Process gender
        gender_map = {'m': 'M', 'male': 'M', 'f': 'F', 'female': 'F'}
        if patient_data.get('gender'):
            patient_data['gender'] = gender_map.get(str(patient_data['gender']).lower(), 'U')
        else:
            patient_data['gender'] = 'U'

        # Process race
        race_map = {
            'white': 'WHITE', 'caucasian': 'WHITE',
            'black': 'BLACK', 'african american': 'BLACK',
            'asian': 'ASIAN', 'pacific islander': 'PACIFIC',
            'native american': 'NATIVE', 'indian': 'NATIVE'
        }
        if patient_data.get('race'):
            patient_data['race'] = race_map.get(str(patient_data['race']).lower(), 'OTHER')
        else:
            patient_data['race'] = 'OTHER'

        # Process zip code
        if patient_data.get('zip_code'):
            zip_str = str(patient_data['zip_code']).strip()
            if len(zip_str) >= 5:
                patient_data['zip_code_prefix'] = zip_str[:5]
            else:
                patient_data['zip_code_prefix'] = '00000'
        else:
            patient_data['zip_code_prefix'] = '00000'

        # Process dates
        if patient_data.get('last_visit_date'):
            try:
                # Try to parse the date
                visit_date = pd.to_datetime(patient_data['last_visit_date']).date()
                patient_data['last_visit_date'] = visit_date
            except:
                patient_data['last_visit_date'] = date.today()
        else:
            patient_data['last_visit_date'] = date.today()

        # Process numeric fields
        numeric_fields = ['emergency_visits', 'hospitalizations']
        for field in numeric_fields:
            if patient_data.get(field):
                try:
                    patient_data[field] = int(patient_data[field])
                except:
                    patient_data[field] = 0
            else:
                patient_data[field] = 0

        # Set defaults for required fields
        if not patient_data.get('primary_diagnosis'):
            patient_data['primary_diagnosis'] = 'General Medical Condition'

        return patient_data, None

    except Exception as e:
        return None, f"Error parsing EMR file: {str(e)}"

@login_required
def upload_emr_patient(request):
    """Upload EMR file and create patient automatically"""
    # Check if user is an HCP
    if request.user.userprofile.role != 'HCP':
        messages.error(request, 'Only Healthcare Providers can upload EMR files.')
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            # Get the HCP profile
            hcp = HCP.objects.get(user=request.user)

            # Check if file was uploaded
            if 'emr_file' not in request.FILES:
                messages.error(request, 'Please select an EMR file to upload.')
                return redirect('add_patient')

            emr_file = request.FILES['emr_file']

            # Parse the EMR file
            patient_data, error = parse_emr_file(emr_file)

            if error:
                messages.error(request, error)
                return redirect('add_patient')

            if not patient_data:
                messages.error(request, 'No patient data could be extracted from the file.')
                return redirect('add_patient')

            # Generate a unique patient ID
            import uuid
            patient_id = f"PAT_{uuid.uuid4().hex[:8].upper()}"

            # Create the patient record
            patient = AnonymizedPatient.objects.create(
                patient_id=patient_id,
                hcp=hcp,
                age_group=patient_data.get('age_group', '26-35'),
                gender=patient_data.get('gender', 'U'),
                race=patient_data.get('race', 'OTHER'),
                ethnicity='NON_HISPANIC',  # Default
                zip_code_prefix=patient_data.get('zip_code_prefix', '00000'),
                primary_diagnosis=patient_data.get('primary_diagnosis', 'General Medical Condition'),
                secondary_diagnoses=patient_data.get('secondary_diagnoses', ''),
                comorbidities=patient_data.get('comorbidities', ''),
                current_treatments=patient_data.get('current_treatments', ''),
                treatment_history=patient_data.get('treatment_history', ''),
                medication_adherence='Good',  # Default
                last_visit_date=patient_data.get('last_visit_date', date.today()),
                visit_frequency='Monthly',  # Default
                emergency_visits_6m=patient_data.get('emergency_visits', 0),
                hospitalizations_6m=patient_data.get('hospitalizations', 0),
                risk_factors=patient_data.get('risk_factors', ''),
                family_history=patient_data.get('family_history', ''),
                insurance_type=patient_data.get('insurance', 'Private'),
                medication_access='Good',  # Default
            )

            # Create EMR data points if additional data exists
            for key, value in patient_data.items():
                if key not in ['age_group', 'gender', 'race', 'zip_code_prefix', 'primary_diagnosis',
                              'secondary_diagnoses', 'comorbidities', 'current_treatments',
                              'treatment_history', 'last_visit_date', 'emergency_visits',
                              'hospitalizations', 'risk_factors', 'family_history'] and value:
                    EMRDataPoint.objects.create(
                        patient=patient,
                        data_type='LAB_RESULT',
                        metric_name=key.replace('_', ' ').title(),
                        value=str(value),
                        date_recorded=date.today(),
                    )

            messages.success(request, f'Patient {patient.patient_id} created successfully from EMR file!')
            return redirect('patient_database')

        except HCP.DoesNotExist:
            messages.error(request, 'HCP profile not found. Please contact support.')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error processing EMR file: {str(e)}')
            return redirect('add_patient')

    return redirect('add_patient')

@login_required
def update_patient(request, patient_id):
    """Update patient information - HCPs only"""
    # Check if user is an HCP
    if request.user.userprofile.role != 'HCP':
        messages.error(request, 'Only Healthcare Providers can update patients.')
        return redirect('patient_detail', patient_id=patient_id)

    try:
        # Get the HCP profile
        hcp = HCP.objects.get(user=request.user)

        # Get the patient and ensure it belongs to this HCP
        patient = get_object_or_404(AnonymizedPatient, patient_id=patient_id, hcp=hcp)

        if request.method == 'POST':
            try:
                # Update patient fields
                patient.age_group = request.POST.get('age_group', patient.age_group)
                patient.gender = request.POST.get('gender', patient.gender)
                patient.race = request.POST.get('race', patient.race)
                patient.ethnicity = request.POST.get('ethnicity', patient.ethnicity)
                patient.zip_code_prefix = request.POST.get('zip_code_prefix', patient.zip_code_prefix)
                patient.primary_diagnosis = request.POST.get('primary_diagnosis', patient.primary_diagnosis)
                patient.secondary_diagnoses = request.POST.get('secondary_diagnoses', patient.secondary_diagnoses)
                patient.comorbidities = request.POST.get('comorbidities', patient.comorbidities)
                patient.current_treatments = request.POST.get('current_treatments', patient.current_treatments)
                patient.treatment_history = request.POST.get('treatment_history', patient.treatment_history)
                patient.medication_adherence = request.POST.get('medication_adherence', patient.medication_adherence)
                patient.last_visit_date = request.POST.get('last_visit_date', patient.last_visit_date)
                patient.visit_frequency = request.POST.get('visit_frequency', patient.visit_frequency)
                patient.emergency_visits_6m = int(request.POST.get('emergency_visits_6m', patient.emergency_visits_6m))
                patient.hospitalizations_6m = int(request.POST.get('hospitalizations_6m', patient.hospitalizations_6m))
                patient.risk_factors = request.POST.get('risk_factors', patient.risk_factors)
                patient.family_history = request.POST.get('family_history', patient.family_history)
                patient.insurance_type = request.POST.get('insurance_type', patient.insurance_type)
                patient.medication_access = request.POST.get('medication_access', patient.medication_access)

                patient.save()
                messages.success(request, f'Patient {patient.patient_id} updated successfully!')
                return redirect('patient_detail', patient_id=patient_id)

            except Exception as e:
                messages.error(request, f'Error updating patient: {str(e)}')

        # If GET request, redirect to patient detail page
        return redirect('patient_detail', patient_id=patient_id)

    except HCP.DoesNotExist:
        messages.error(request, 'HCP profile not found. Please contact support.')
        return redirect('dashboard')

@login_required
def delete_patient(request, patient_id):
    """Delete patient - HCPs only"""
    # Check if user is an HCP
    if request.user.userprofile.role != 'HCP':
        messages.error(request, 'Only Healthcare Providers can delete patients.')
        return redirect('patient_detail', patient_id=patient_id)

    try:
        # Get the HCP profile
        hcp = HCP.objects.get(user=request.user)

        # Get the patient and ensure it belongs to this HCP
        patient = get_object_or_404(AnonymizedPatient, patient_id=patient_id, hcp=hcp)

        if request.method == 'POST':
            try:
                patient_id_backup = patient.patient_id
                patient.delete()
                messages.success(request, f'Patient {patient_id_backup} has been deleted successfully.')
                return redirect('patient_database')
            except Exception as e:
                messages.error(request, f'Error deleting patient: {str(e)}')
                return redirect('patient_detail', patient_id=patient_id)

        # If GET request, redirect to patient detail page
        return redirect('patient_detail', patient_id=patient_id)

    except HCP.DoesNotExist:
        messages.error(request, 'HCP profile not found. Please contact support.')
        return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'Error deleting patient: {str(e)}')
        return redirect('patient_detail', patient_id=patient_id)

    # If GET request, redirect to patient detail page
    return redirect('patient_detail', patient_id=patient_id)


# New Research and Recommendation System Functions

def analyze_patient_issues(hcp_id):
    """Analyze common issues across a doctor's patients"""
    hcp = get_object_or_404(HCP, id=hcp_id)
    
    # Get all patients for this HCP (limit to first 100 for performance)
    patients = AnonymizedPatient.objects.filter(hcp=hcp)[:100]
    
    if not patients.exists():
        return None
    
    print(f"📊 Analyzing {len(patients)} patients for {hcp.name}")
    
    # Analyze common diagnoses
    diagnoses = []
    treatments = []
    comorbidities = []
    risk_factors = []
    
    for patient in patients:
        if patient.primary_diagnosis:
            diagnoses.append(patient.primary_diagnosis)
        if patient.secondary_diagnoses:
            diagnoses.extend(patient.secondary_diagnoses.split(','))
        if patient.current_treatments:
            treatments.extend(patient.current_treatments.split(','))
        if patient.comorbidities:
            comorbidities.extend(patient.comorbidities.split(','))
        if patient.risk_factors:
            risk_factors.extend(patient.risk_factors.split(','))
    
    print(f"🔍 Found {len(diagnoses)} diagnoses, {len(treatments)} treatments")
    
    # Count frequencies
    diagnosis_counts = Counter([d.strip() for d in diagnoses if d.strip()])
    treatment_counts = Counter([t.strip() for t in treatments if t.strip()])
    comorbidity_counts = Counter([c.strip() for c in comorbidities if c.strip()])
    risk_factor_counts = Counter([r.strip() for r in risk_factors if r.strip()])
    
    # Identify treatment gaps (common diagnoses without corresponding treatments)
    treatment_gaps = []
    for diagnosis in diagnosis_counts.most_common(5):
        diagnosis_name = diagnosis[0].lower()
        has_treatment = any(diagnosis_name in treatment.lower() for treatment in treatment_counts.keys())
        if not has_treatment:
            treatment_gaps.append({
                'diagnosis': diagnosis[0],
                'frequency': diagnosis[1],
                'percentage': round((diagnosis[1] / len(patients)) * 100, 1)
            })
    
    # Create analysis summary
    analysis_summary = f"""
    Analysis of {len(patients)} patients under {hcp.name}'s care:
    
    Top Diagnoses:
    {', '.join([f"{d[0]} ({d[1]} patients)" for d in diagnosis_counts.most_common(3)])}
    
    Treatment Gaps Identified:
    {', '.join([f"{gap['diagnosis']} ({gap['percentage']}% of patients)" for gap in treatment_gaps[:3]])}
    
    Common Risk Factors:
    {', '.join([f"{r[0]} ({r[1]} patients)" for r in risk_factor_counts.most_common(3)])}
    """
    
    # Create PatientIssueAnalysis object
    analysis = PatientIssueAnalysis.objects.create(
        hcp=hcp,
        total_patients_analyzed=len(patients),
        common_issues=[
            {'issue': item[0], 'frequency': item[1], 'percentage': round((item[1] / len(patients)) * 100, 1)}
            for item in diagnosis_counts.most_common(10)
        ],
        top_diagnoses=[
            {'diagnosis': item[0], 'frequency': item[1], 'percentage': round((item[1] / len(patients)) * 100, 1)}
            for item in diagnosis_counts.most_common(5)
        ],
        treatment_gaps=treatment_gaps,
        risk_factors=[
            {'risk_factor': item[0], 'frequency': item[1], 'percentage': round((item[1] / len(patients)) * 100, 1)}
            for item in risk_factor_counts.most_common(5)
        ],
        analysis_summary=analysis_summary.strip()
    )
    
    return analysis


def scrape_medical_research(keywords, specialty=None, max_results=10):
    """Scrape medical research articles based on keywords from patient issues"""
    scraped_articles = []
    
    # Enhanced research database with more comprehensive articles
    research_database = [
        # Diabetes-related articles
        {
            'title': 'Novel Treatment Approaches for Diabetes Management',
            'authors': 'Smith, J., Johnson, A., Brown, K.',
            'journal': 'New England Journal of Medicine',
            'publication_date': '2024-01-15',
            'abstract': 'This study examines new treatment modalities for diabetes management, including SGLT-2 inhibitors and GLP-1 receptor agonists.',
            'keywords': ['diabetes', 'treatment', 'SGLT-2', 'GLP-1', 'metformin'],
            'conditions': ['diabetes', 'type 2 diabetes', 'diabetic'],
            'treatments': ['SGLT-2 inhibitors', 'GLP-1 receptor agonists', 'metformin'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example1',
            'relevance_score': 0.95
        },
        {
            'title': 'Cardiovascular Outcomes in Hypertension Treatment',
            'authors': 'Williams, M., Davis, R.',
            'journal': 'Journal of the American Medical Association',
            'publication_date': '2024-02-01',
            'abstract': 'Comprehensive analysis of cardiovascular outcomes in patients treated with ACE inhibitors vs ARBs.',
            'keywords': ['hypertension', 'cardiovascular', 'ACE inhibitors', 'ARBs', 'blood pressure'],
            'conditions': ['hypertension', 'cardiovascular disease', 'high blood pressure'],
            'treatments': ['ACE inhibitors', 'ARBs', 'beta blockers'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example2',
            'relevance_score': 0.88
        },
        {
            'title': 'Innovations in Cancer Immunotherapy',
            'authors': 'Garcia, L., Martinez, P.',
            'journal': 'Nature Medicine',
            'publication_date': '2024-01-20',
            'abstract': 'Recent advances in cancer immunotherapy and their clinical applications.',
            'keywords': ['cancer', 'immunotherapy', 'oncology', 'tumor'],
            'conditions': ['cancer', 'tumor', 'oncology'],
            'treatments': ['immunotherapy', 'checkpoint inhibitors', 'chemotherapy'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example3',
            'relevance_score': 0.92
        },
        # Heart-related articles
        {
            'title': 'Advanced Heart Failure Management Strategies',
            'authors': 'Chen, L., Rodriguez, M.',
            'journal': 'Circulation',
            'publication_date': '2024-01-10',
            'abstract': 'New approaches to managing heart failure including device therapy and novel medications.',
            'keywords': ['heart failure', 'cardiology', 'device therapy', 'heart'],
            'conditions': ['heart failure', 'cardiac', 'cardiomyopathy'],
            'treatments': ['ACE inhibitors', 'beta blockers', 'device therapy'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example4',
            'relevance_score': 0.89
        },
        # Mental health articles
        {
            'title': 'Depression Treatment in Primary Care Settings',
            'authors': 'Thompson, K., Lee, S.',
            'journal': 'Journal of Clinical Psychiatry',
            'publication_date': '2024-02-15',
            'abstract': 'Evidence-based approaches to treating depression in primary care with focus on SSRIs and therapy.',
            'keywords': ['depression', 'mental health', 'SSRI', 'therapy'],
            'conditions': ['depression', 'mental health', 'anxiety'],
            'treatments': ['SSRIs', 'therapy', 'counseling'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example5',
            'relevance_score': 0.87
        },
        # Respiratory articles
        {
            'title': 'COPD Management in the Modern Era',
            'authors': 'Anderson, R., Wilson, T.',
            'journal': 'American Journal of Respiratory Medicine',
            'publication_date': '2024-01-25',
            'abstract': 'Comprehensive review of COPD treatment including bronchodilators and pulmonary rehabilitation.',
            'keywords': ['COPD', 'respiratory', 'bronchodilator', 'lung'],
            'conditions': ['COPD', 'respiratory', 'lung disease'],
            'treatments': ['bronchodilators', 'inhalers', 'pulmonary rehabilitation'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example6',
            'relevance_score': 0.91
        },
        # Gastrointestinal articles
        {
            'title': 'GERD Treatment Options and Outcomes',
            'authors': 'Patel, N., Kumar, V.',
            'journal': 'Gastroenterology',
            'publication_date': '2024-02-05',
            'abstract': 'Review of GERD management including PPIs, lifestyle modifications, and surgical options.',
            'keywords': ['GERD', 'gastrointestinal', 'PPI', 'acid reflux'],
            'conditions': ['GERD', 'acid reflux', 'gastrointestinal'],
            'treatments': ['PPIs', 'H2 blockers', 'lifestyle modifications'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example7',
            'relevance_score': 0.86
        },
        # Neurological articles
        {
            'title': 'Migraine Management: New Therapeutic Approaches',
            'authors': 'Johnson, A., Smith, B.',
            'journal': 'Neurology',
            'publication_date': '2024-01-30',
            'abstract': 'Recent advances in migraine treatment including CGRP antagonists and neuromodulation techniques.',
            'keywords': ['migraine', 'neurology', 'CGRP', 'headache'],
            'conditions': ['migraine', 'headache', 'neurological'],
            'treatments': ['CGRP antagonists', 'triptans', 'neuromodulation'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example8',
            'relevance_score': 0.88
        },
        # Additional diverse articles for more variety
        {
            'title': 'Precision Medicine in Rheumatoid Arthritis',
            'authors': 'Davis, M., Wilson, K.',
            'journal': 'Arthritis & Rheumatism',
            'publication_date': '2024-02-10',
            'abstract': 'Personalized treatment approaches for rheumatoid arthritis using biomarkers and targeted therapies.',
            'keywords': ['rheumatoid arthritis', 'precision medicine', 'biomarkers', 'DMARDs'],
            'conditions': ['rheumatoid arthritis', 'autoimmune', 'joint disease'],
            'treatments': ['DMARDs', 'biologics', 'methotrexate'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example9',
            'relevance_score': 0.90
        },
        {
            'title': 'Chronic Kidney Disease: Early Detection and Management',
            'authors': 'Brown, T., Garcia, L.',
            'journal': 'Kidney International',
            'publication_date': '2024-01-18',
            'abstract': 'Strategies for early detection and management of chronic kidney disease progression.',
            'keywords': ['kidney disease', 'CKD', 'nephrology', 'renal'],
            'conditions': ['chronic kidney disease', 'renal failure', 'nephropathy'],
            'treatments': ['ACE inhibitors', 'diet modification', 'dialysis'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example10',
            'relevance_score': 0.85
        },
        {
            'title': 'Obesity Management: Multidisciplinary Approaches',
            'authors': 'Martinez, P., Lee, J.',
            'journal': 'Obesity Reviews',
            'publication_date': '2024-02-12',
            'abstract': 'Comprehensive approaches to obesity management including lifestyle, pharmacotherapy, and surgery.',
            'keywords': ['obesity', 'weight management', 'bariatric', 'metabolic'],
            'conditions': ['obesity', 'metabolic syndrome', 'weight gain'],
            'treatments': ['lifestyle modification', 'GLP-1 agonists', 'bariatric surgery'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example11',
            'relevance_score': 0.87
        },
        {
            'title': 'Thyroid Disorders: Diagnosis and Treatment Updates',
            'authors': 'Chen, W., Rodriguez, S.',
            'journal': 'Endocrine Reviews',
            'publication_date': '2024-01-22',
            'abstract': 'Updated guidelines for diagnosis and treatment of thyroid disorders including hypothyroidism and hyperthyroidism.',
            'keywords': ['thyroid', 'hypothyroidism', 'hyperthyroidism', 'TSH'],
            'conditions': ['hypothyroidism', 'hyperthyroidism', 'thyroid disease'],
            'treatments': ['levothyroxine', 'methimazole', 'radioactive iodine'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example12',
            'relevance_score': 0.89
        },
        {
            'title': 'Infectious Disease Prevention in Healthcare Settings',
            'authors': 'Thompson, R., Anderson, M.',
            'journal': 'Infection Control & Hospital Epidemiology',
            'publication_date': '2024-02-08',
            'abstract': 'Best practices for preventing healthcare-associated infections and antimicrobial resistance.',
            'keywords': ['infection control', 'antimicrobial resistance', 'healthcare', 'prevention'],
            'conditions': ['healthcare-associated infections', 'antimicrobial resistance'],
            'treatments': ['infection control', 'antimicrobial stewardship', 'vaccination'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example13',
            'relevance_score': 0.84
        },
        {
            'title': 'Dermatology: Advances in Skin Cancer Detection',
            'authors': 'Wilson, A., Patel, K.',
            'journal': 'Journal of the American Academy of Dermatology',
            'publication_date': '2024-01-28',
            'abstract': 'New technologies and approaches for early detection and treatment of skin cancer.',
            'keywords': ['skin cancer', 'melanoma', 'dermatology', 'detection'],
            'conditions': ['skin cancer', 'melanoma', 'basal cell carcinoma'],
            'treatments': ['surgical excision', 'immunotherapy', 'targeted therapy'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example14',
            'relevance_score': 0.86
        },
        {
            'title': 'Pediatric Asthma: Management Strategies',
            'authors': 'Lee, H., Kumar, R.',
            'journal': 'Pediatrics',
            'publication_date': '2024-02-14',
            'abstract': 'Evidence-based approaches to managing asthma in pediatric populations.',
            'keywords': ['pediatric asthma', 'children', 'respiratory', 'inhalers'],
            'conditions': ['pediatric asthma', 'childhood respiratory disease'],
            'treatments': ['inhaled corticosteroids', 'bronchodilators', 'education'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example15',
            'relevance_score': 0.88
        },
        {
            'title': 'Geriatric Medicine: Comprehensive Care Approaches',
            'authors': 'Smith, D., Johnson, E.',
            'journal': 'Journal of the American Geriatrics Society',
            'publication_date': '2024-01-12',
            'abstract': 'Holistic approaches to caring for elderly patients with multiple comorbidities.',
            'keywords': ['geriatrics', 'elderly', 'comorbidities', 'polypharmacy'],
            'conditions': ['multiple comorbidities', 'geriatric syndromes', 'frailty'],
            'treatments': ['comprehensive assessment', 'medication review', 'functional support'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example16',
            'relevance_score': 0.83
        },
        {
            'title': 'Women\'s Health: Menopause Management Updates',
            'authors': 'Garcia, M., Davis, L.',
            'journal': 'Menopause',
            'publication_date': '2024-02-18',
            'abstract': 'Current approaches to managing menopausal symptoms and long-term health outcomes.',
            'keywords': ['menopause', 'hormone therapy', 'women\'s health', 'osteoporosis'],
            'conditions': ['menopause', 'hot flashes', 'osteoporosis'],
            'treatments': ['hormone therapy', 'non-hormonal treatments', 'lifestyle modifications'],
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/example17',
            'relevance_score': 0.85
        }
    ]
    
    # Filter articles based on keywords and specialty
    for article in research_database:
        relevance_score = 0.0
        
        # Check keyword matches in multiple fields
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Check in abstract
            if keyword_lower in article['abstract'].lower():
                relevance_score += 0.4
            
            # Check in keywords list
            if any(keyword_lower in kw.lower() for kw in article['keywords']):
                relevance_score += 0.3
            
            # Check in conditions
            if any(keyword_lower in cond.lower() for cond in article['conditions']):
                relevance_score += 0.3
            
            # Check in treatments
            if any(keyword_lower in treat.lower() for treat in article['treatments']):
                relevance_score += 0.2
        
        # Check specialty match
        if specialty:
            specialty_lower = specialty.lower()
            if specialty_lower in article['abstract'].lower():
                relevance_score += 0.2
            if specialty_lower in article['journal'].lower():
                relevance_score += 0.1
        
        # Only include articles with sufficient relevance
        if relevance_score >= 0.3:
            article['relevance_score'] = min(relevance_score, 1.0)
            scraped_articles.append(article)
    
    # Sort by relevance score
    scraped_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # Save to database
    saved_articles = []
    for article_data in scraped_articles[:max_results]:
        article, created = ScrapedResearch.objects.get_or_create(
            title=article_data['title'],
            defaults={
                'authors': article_data['authors'],
                'journal': article_data['journal'],
                'publication_date': article_data['publication_date'],
                'abstract': article_data['abstract'],
                'keywords': article_data['keywords'],
                'specialties': [specialty] if specialty else [],
                'conditions_mentioned': article_data['conditions'],
                'treatments_mentioned': article_data['treatments'],
                'source_url': article_data['source_url'],
                'relevance_score': article_data['relevance_score']
            }
        )
        saved_articles.append(article)
    
    return saved_articles


def generate_intelligent_recommendation(hcp_id, hcr_user):
    """Generate intelligent recommendation combining patient analysis and research"""
    hcp = get_object_or_404(HCP, id=hcp_id)
    
    # Step 1: Analyze patient issues
    analysis = analyze_patient_issues(hcp_id)
    if not analysis:
        return None
    
    # Step 2: Extract keywords from analysis
    keywords = []
    for issue in analysis.common_issues[:5]:  # Top 5 issues
        keywords.append(issue['issue'])
    
    for gap in analysis.treatment_gaps[:3]:  # Top 3 treatment gaps
        keywords.append(gap['diagnosis'])
    
    # Step 3: Scrape relevant research
    relevant_research = scrape_medical_research(keywords, hcp.specialty, max_results=5)
    
    # Step 4: Find relevant cluster insights
    cluster_insights = PatientCluster.objects.filter(hcp=hcp).first()
    
    # Step 5: Generate recommendation
    if analysis.treatment_gaps:
        top_gap = analysis.treatment_gaps[0]
        recommendation_title = f"Treatment Optimization for {top_gap['diagnosis']}"
        
        recommendation_summary = f"""
        Based on analysis of {analysis.total_patients_analyzed} patients, {top_gap['percentage']}% 
        have {top_gap['diagnosis']} but may not be receiving optimal treatment. Recent research 
        suggests new approaches that could improve patient outcomes.
        """
        
        # Combine evidence
        evidence_summary = f"""
        Patient Data Evidence:
        - {top_gap['frequency']} patients ({top_gap['percentage']}%) diagnosed with {top_gap['diagnosis']}
        - Common risk factors: {', '.join([rf['risk_factor'] for rf in analysis.risk_factors[:3]])}
        
        Research Evidence:
        {chr(10).join([f"- {research.title} (Relevance: {research.relevance_score:.2f})" for research in relevant_research[:3]])}
        
        Cluster Analysis:
        - Similar patients in cluster show {cluster_insights.success_rate if cluster_insights else 'N/A'}% treatment success rate
        """
        
        # Create intelligent recommendation
        recommendation = IntelligentRecommendation.objects.create(
            hcp=hcp,
            hcr_sender=hcr_user,
            patient_analysis=analysis,
            cluster_insights=cluster_insights,
            recommendation_title=recommendation_title,
            recommendation_summary=recommendation_summary.strip(),
            evidence_summary=evidence_summary.strip(),
            patient_data_evidence={
                'total_patients': analysis.total_patients_analyzed,
                'top_issues': analysis.common_issues[:5],
                'treatment_gaps': analysis.treatment_gaps[:3],
                'risk_factors': analysis.risk_factors[:5]
            },
            research_evidence=[
                {
                    'title': research.title,
                    'relevance_score': research.relevance_score,
                    'abstract': research.abstract[:200] + '...' if len(research.abstract) > 200 else research.abstract
                }
                for research in relevant_research[:3]
            ],
            cluster_evidence={
                'cluster_id': cluster_insights.id if cluster_insights else None,
                'success_rate': cluster_insights.success_rate if cluster_insights else None,
                'patient_count': cluster_insights.patient_count if cluster_insights else None
            },
            priority='HIGH' if top_gap['percentage'] > 30 else 'MEDIUM'
        )
        
        # Add research articles to recommendation
        recommendation.relevant_research.set(relevant_research)
        
        return recommendation
    
    return None


def generate_cluster_based_recommendation(hcp_id, hcr_user, cluster_data):
    """Generate recommendation based on specific cluster data from network"""
    hcp = get_object_or_404(HCP, id=hcp_id)
    cluster = cluster_data['cluster']
    
    # Extract keywords from cluster data
    keywords = []
    if cluster_data['common_treatments']:
        keywords.extend(cluster_data['common_treatments'][:3])  # Top 3 treatments
    if cluster_data['diagnoses']:
        keywords.extend(cluster_data['diagnoses'][:3])  # Top 3 diagnoses
    
    # Scrape relevant research
    relevant_research = scrape_medical_research(keywords, hcp.specialty, max_results=3)
    
    # Create recommendation based on cluster insights
    recommendation_title = f"Treatment Optimization for {cluster_data['cluster_name']}"
    
    recommendation_summary = f"""
    Based on analysis of your {cluster_data['cluster_name']} cluster with {cluster_data['patient_count']} patients 
    showing {cluster_data['success_rate']}% treatment success rate, we've identified opportunities to improve 
    patient outcomes through evidence-based treatment approaches.
    """
    
    # Combine evidence
    evidence_summary = f"""
    Cluster Analysis Evidence:
    - Cluster: {cluster_data['cluster_name']}
    - Patient Count: {cluster_data['patient_count']} patients
    - Current Success Rate: {cluster_data['success_rate']}%
    - Common Treatments: {', '.join(cluster_data['common_treatments'][:3]) if cluster_data['common_treatments'] else 'N/A'}
    - Primary Diagnoses: {', '.join(cluster_data['diagnoses'][:3]) if cluster_data['diagnoses'] else 'N/A'}
    
    Research Evidence:
    {chr(10).join([f"- {research.title} (Relevance: {research.relevance_score:.2f})" for research in relevant_research[:2]])}
    
    Recommendation:
    Consider implementing the following evidence-based treatments that have shown success 
    in similar patient clusters, potentially improving your success rate from {cluster_data['success_rate']}% 
    to 85%+ based on cluster analysis.
    """
    
    # Create patient analysis for the recommendation
    analysis = PatientIssueAnalysis.objects.create(
        hcp=hcp,
        total_patients_analyzed=cluster_data['patient_count'],
        common_issues=[
            {'issue': diagnosis, 'frequency': cluster_data['patient_count'] // len(cluster_data['diagnoses']) if cluster_data['diagnoses'] else 1, 'percentage': 100.0}
            for diagnosis in cluster_data['diagnoses'][:5]
        ],
        top_diagnoses=[
            {'diagnosis': diagnosis, 'frequency': cluster_data['patient_count'] // len(cluster_data['diagnoses']) if cluster_data['diagnoses'] else 1, 'percentage': 100.0}
            for diagnosis in cluster_data['diagnoses'][:3]
        ],
        treatment_gaps=[
            {'diagnosis': diagnosis, 'frequency': cluster_data['patient_count'] // len(cluster_data['diagnoses']) if cluster_data['diagnoses'] else 1, 'percentage': 100.0}
            for diagnosis in cluster_data['diagnoses'][:2]
        ],
        risk_factors=[],
        analysis_summary=f"Cluster-based analysis for {cluster_data['cluster_name']} with {cluster_data['patient_count']} patients"
    )
    
    # Create intelligent recommendation
    recommendation = IntelligentRecommendation.objects.create(
        hcp=hcp,
        hcr_sender=hcr_user,
        patient_analysis=analysis,
        cluster_insights=cluster,
        recommendation_title=recommendation_title,
        recommendation_summary=recommendation_summary.strip(),
        evidence_summary=evidence_summary.strip(),
        patient_data_evidence={
            'total_patients': cluster_data['patient_count'],
            'cluster_name': cluster_data['cluster_name'],
            'success_rate': cluster_data['success_rate'],
            'common_treatments': cluster_data['common_treatments'][:5],
            'diagnoses': cluster_data['diagnoses'][:5]
        },
        research_evidence=[
            {
                'title': research.title,
                'relevance_score': research.relevance_score,
                'abstract': research.abstract[:200] + '...' if len(research.abstract) > 200 else research.abstract
            }
            for research in relevant_research[:2]
        ],
        cluster_evidence={
            'cluster_id': cluster.id,
            'success_rate': cluster_data['success_rate'],
            'patient_count': cluster_data['patient_count'],
            'cluster_name': cluster_data['cluster_name']
        },
        priority='HIGH' if cluster_data['success_rate'] < 70 else 'MEDIUM'
    )
    
    # Add research articles to recommendation
    recommendation.relevant_research.set(relevant_research)
    
    return recommendation


@login_required
def create_recommendation(request, hcp_id):
    """Create and send intelligent recommendation to HCP"""
    if request.user.userprofile.role != 'HCR':
        messages.error(request, 'Only Healthcare Representatives can create recommendations.')
        return redirect('dashboard')
    
    hcp = get_object_or_404(HCP, id=hcp_id)
    
    # Check if this is coming from cluster network selection
    cluster_data = None
    if request.method == 'GET' and 'cluster_id' in request.GET:
        cluster_id = request.GET.get('cluster_id')
        try:
            cluster = PatientCluster.objects.get(id=cluster_id, hcp=hcp)
            cluster_data = {
                'cluster': cluster,
                'cluster_name': cluster.name,
                'patient_count': cluster.patient_count,
                'success_rate': cluster.success_rate,
                'common_treatments': cluster.common_treatments,
                'diagnoses': cluster.diagnoses
            }
        except PatientCluster.DoesNotExist:
            messages.error(request, 'Selected cluster not found.')
            return redirect('cohort_cluster_network')
    
    # Generate recommendation (either from cluster data or full analysis)
    if cluster_data:
        recommendation = generate_cluster_based_recommendation(hcp_id, request.user, cluster_data)
    else:
        recommendation = generate_intelligent_recommendation(hcp_id, request.user)
    
    if recommendation:
        messages.success(request, f'Intelligent recommendation created for {recommendation.hcp.name}')
        return redirect('view_recommendation', recommendation_id=recommendation.id)
    else:
        messages.error(request, 'Unable to create recommendation. Insufficient patient data.')
        return redirect('hcp_profile', hcp_id=hcp_id)


@login_required
def delete_recommendation(request, recommendation_id):
    """Delete a draft recommendation"""
    if request.user.userprofile.role != 'HCR':
        return JsonResponse({'success': False, 'error': 'Only Healthcare Representatives can delete recommendations.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})
    
    try:
        recommendation = get_object_or_404(IntelligentRecommendation, id=recommendation_id)
        
        # Check if user owns this recommendation
        if recommendation.hcr_sender != request.user:
            return JsonResponse({'success': False, 'error': 'You can only delete your own recommendations.'})
        
        # Only allow deletion of draft recommendations
        if recommendation.status != 'DRAFT':
            return JsonResponse({'success': False, 'error': 'Only draft recommendations can be deleted.'})
        
        # Delete the recommendation
        recommendation.delete()
        
        return JsonResponse({'success': True, 'message': 'Recommendation deleted successfully.'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error deleting recommendation: {str(e)}'})


@login_required
def edit_recommendation(request, recommendation_id):
    """Edit an existing recommendation"""
    recommendation = get_object_or_404(IntelligentRecommendation, id=recommendation_id)
    
    # Check if user is HCR and owns this recommendation
    if not (request.user.userprofile.role == 'HCR' and recommendation.hcr_sender == request.user):
        messages.error(request, "You don't have permission to edit this recommendation.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Update the recommendation with new data
        recommendation.recommendation_title = request.POST.get('title', recommendation.recommendation_title)
        recommendation.recommendation_summary = request.POST.get('summary', recommendation.recommendation_summary)
        recommendation.priority = request.POST.get('priority', recommendation.priority)
        recommendation.evidence_summary = request.POST.get('evidence_summary', recommendation.evidence_summary)
        recommendation.save()
        
        messages.success(request, "Recommendation updated successfully!")
        return redirect('view_recommendation', recommendation_id=recommendation.id)
    
    context = {
        'recommendation': recommendation,
        'is_hcr': request.user.userprofile.role == 'HCR'
    }
    return render(request, 'core/edit_recommendation.html', context)


@login_required
def view_recommendation(request, recommendation_id):
    try:
        recommendation = IntelligentRecommendation.objects.get(id=recommendation_id)
    except IntelligentRecommendation.DoesNotExist:
        messages.error(request, f'Recommendation with ID {recommendation_id} not found.')
        return redirect('dashboard')
    
    # Check permissions
    if request.user.userprofile.role == 'HCR' and recommendation.hcr_sender != request.user:
        messages.error(request, 'You can only view your own recommendations.')
        return redirect('dashboard')
    
    context = {
        'recommendation': recommendation,
        'is_hcr': request.user.userprofile.role == 'HCR',
        'is_hcp': request.user.userprofile.role == 'HCP'
    }
    
    return render(request, 'core/recommendation_detail.html', context)


@login_required
def send_recommendation_message(request, recommendation_id):
    """Send recommendation as message to HCP"""
    if request.user.userprofile.role != 'HCR':
        messages.error(request, 'Only Healthcare Representatives can send messages.')
        return redirect('dashboard')
    
    recommendation = get_object_or_404(IntelligentRecommendation, id=recommendation_id)
    
    if request.method == 'POST':
        subject = request.POST.get('subject', recommendation.recommendation_title)
        message_content = request.POST.get('message_content', recommendation.recommendation_summary)
        
        # Create HCRRecommendation for the HCP dashboard
        hcr_recommendation = HCRRecommendation.objects.create(
            hcp_user=recommendation.hcp.user,
            title=subject,
            message=message_content,
            priority='HIGH' if recommendation.priority == 'HIGH' else 'MEDIUM',
            research_update=None  # We can link this later if needed
        )
        
        # Also create message for record keeping
        message = HCRMessage.objects.create(
            sender=request.user,
            recipient_hcp=recommendation.hcp,
            message_type='RECOMMENDATION',
            subject=subject,
            message_content=message_content,
            recommendation=recommendation
        )
        
        # Update recommendation status
        recommendation.status = 'SENT'
        recommendation.sent_date = timezone.now()
        recommendation.save()
        
        messages.success(request, f'Recommendation sent to {recommendation.hcp.name}')
        return redirect('dashboard')
    
    context = {
        'recommendation': recommendation
    }
    
    return render(request, 'core/send_recommendation.html', context)


@login_required
def generate_recommendation_page(request):
    """Page for selecting HCP and generating recommendations"""
    if request.user.userprofile.role != 'HCR':
        messages.error(request, 'Only Healthcare Representatives can generate recommendations.')
        return redirect('dashboard')
    
    # Get all HCPs with patient counts and last contact dates
    hcps = []
    for hcp in HCP.objects.all():
        # Count patients for this HCP
        patient_count = AnonymizedPatient.objects.filter(hcp=hcp).count()
        
        # Get last engagement date
        last_engagement = Engagement.objects.filter(hcp=hcp).order_by('-date').first()
        last_contact = last_engagement.date if last_engagement else None
        
        hcps.append({
            'id': hcp.id,
            'name': hcp.name,
            'specialty': hcp.specialty,
            'contact_info': hcp.contact_info,
            'patient_count': patient_count,
            'last_contact': last_contact
        })
    
    context = {
        'hcps': hcps
    }
    
    return render(request, 'core/generate_recommendation.html', context)


@login_required
def create_recommendation_ajax(request, hcp_id):
    """AJAX endpoint for creating recommendations"""
    if request.user.userprofile.role != 'HCR':
        return JsonResponse({'success': False, 'error': 'Only Healthcare Representatives can create recommendations.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})
    
    try:
        print(f"🚀 Starting recommendation generation for HCP {hcp_id}")
        
        # Check if HCP exists
        hcp = get_object_or_404(HCP, id=hcp_id)
        print(f"✅ Found HCP: {hcp.name}")
        
        # Check if HCP has patients
        patient_count = AnonymizedPatient.objects.filter(hcp=hcp).count()
        print(f"📊 HCP has {patient_count} patients")
        
        if patient_count == 0:
            return JsonResponse({'success': False, 'error': f'No patients found for {hcp.name}. Cannot generate recommendations without patient data.'})
        
        recommendation = generate_intelligent_recommendation(hcp_id, request.user)
        
        if recommendation:
            print(f"✅ Recommendation created: {recommendation.recommendation_title}")
            
            # Get research articles for the modal
            research_articles = []
            for research in recommendation.relevant_research.all()[:3]:
                research_articles.append({
                    'title': research.title,
                    'authors': research.authors,
                    'journal': research.journal,
                    'publication_date': research.publication_date,
                    'source_url': research.source_url
                })
            
            return JsonResponse({
                'success': True,
                'recommendation_title': recommendation.recommendation_title,
                'redirect_url': f'/dashboard/recommendation/{recommendation.id}/',
                'research_articles': research_articles
            })
        else:
            return JsonResponse({'success': False, 'error': 'Unable to create recommendation. No treatment gaps found in patient data.'})
    
    except Exception as e:
        print(f"❌ Error generating recommendation: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Error generating recommendation: {str(e)}'})

@login_required
def hcr_recommendations(request):
    """Display HCR recommendations for the current HCP"""
    try:
        # Get all recommendations for the current user (HCP)
        recommendations = HCRRecommendation.objects.filter(hcp_user=request.user).order_by('-created_date')
        
        # Get unread count
        unread_count = recommendations.filter(is_read=False).count()
        
        # Pagination
        from django.core.paginator import Paginator
        paginator = Paginator(recommendations, 10)  # Show 10 per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'recommendations': page_obj,
            'unread_count': unread_count,
            'page_title': 'HCR Recommendations'
        }
        
        return render(request, 'core/hcr_recommendations.html', context)
        
    except Exception as e:
        print(f"❌ Error loading HCR recommendations: {str(e)}")
        return render(request, 'core/hcr_recommendations.html', {
            'recommendations': [],
            'unread_count': 0,
            'error': f'Error loading recommendations: {str(e)}'
        })

@require_http_methods(["POST"])
@login_required
def mark_recommendation_read(request, recommendation_id):
    """Mark a recommendation as read"""
    try:
        recommendation = get_object_or_404(HCRRecommendation, id=recommendation_id, hcp_user=request.user)
        recommendation.is_read = True
        recommendation.save()
        
        return JsonResponse({'success': True, 'message': 'Recommendation marked as read'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
@login_required
def accept_recommendation(request, recommendation_id):
    """Accept a recommendation"""
    try:
        recommendation = get_object_or_404(HCRRecommendation, id=recommendation_id, hcp_user=request.user)
        recommendation.status = 'ACCEPTED'
        recommendation.is_read = True
        recommendation.save()
        
        return JsonResponse({'success': True, 'message': 'Recommendation accepted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
@login_required
def decline_recommendation(request, recommendation_id):
    """Decline a recommendation"""
    try:
        recommendation = get_object_or_404(HCRRecommendation, id=recommendation_id, hcp_user=request.user)
        recommendation.status = 'DECLINED'
        recommendation.is_read = True
        recommendation.save()
        
        return JsonResponse({'success': True, 'message': 'Recommendation declined'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_recommendation_research(request, recommendation_id):
    """Get research articles for a specific recommendation"""
    try:
        recommendation = get_object_or_404(HCRRecommendation, id=recommendation_id, hcp_user=request.user)
        
        # Get research articles associated with this recommendation
        research_articles = []
        for research in recommendation.relevant_research.all()[:3]:
            research_articles.append({
                'title': research.title,
                'authors': research.authors,
                'journal': research.journal,
                'publication_date': research.publication_date,
                'source_url': research.source_url
            })
        
        return JsonResponse({
            'success': True,
            'research_articles': research_articles
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
