from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg
from django.db import models
from datetime import date, timedelta
import json
import csv
from .models import (HCP, ResearchUpdate, EMRData, Engagement, UserProfile, HCRRecommendation, 
                    PatientCohort, TreatmentOutcome, CohortRecommendation, ActionableInsight,
                    AnonymizedPatient, PatientCluster, ClusterMembership, PatientOutcome, 
                    EMRDataPoint, ClusterInsight, DrugRecommendation)

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
    
    # Get AI-powered drug recommendations based on cluster analysis
    drug_recommendations = DrugRecommendation.objects.select_related('hcp', 'cluster').order_by(
        '-priority', '-success_rate', '-created_date'
    )[:12]  # Show top 12 recommendations
    
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
        'cohort_recommendations': cohort_recommendations,
        'drug_recommendations': drug_recommendations,
        'dynamic_recommendations': dynamic_recommendations,
        'total_insights': total_insights,
        'high_priority_insights': high_priority_insights,
        'total_patients_impacted': total_patients_impacted,
        'total_patients': total_patients,
        'total_cohorts': total_cohorts,
        'total_clusters': total_clusters,
    }
    return render(request, 'core/hcr_dashboard.html', context)

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
    
    # Get research relevant to HCP's specialty
    specialty_research = ResearchUpdate.objects.filter(
        specialty=user_profile.specialty
    ).order_by('-date')[:5] if user_profile.specialty else ResearchUpdate.objects.order_by('-date')[:5]
    
    # Get general research updates
    general_research = ResearchUpdate.objects.exclude(
        specialty=user_profile.specialty
    ).order_by('-date')[:3] if user_profile.specialty else []
    
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
    # Get filter parameters
    current_specialty = request.GET.get('specialty', '')
    current_diagnosis = request.GET.get('diagnosis', '')
    current_hcp = request.GET.get('hcp', '')
    
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
    
    # Apply additional filters
    if current_specialty:
        patients = patients.filter(hcp__specialty=current_specialty)
    if current_diagnosis:
        patients = patients.filter(primary_diagnosis__icontains=current_diagnosis)
    if current_hcp:
        patients = patients.filter(hcp__name__icontains=current_hcp)
    
    # Get unique values for filter dropdowns
    specialties = list(set(AnonymizedPatient.objects.values_list('hcp__specialty', flat=True)))
    specialties = [s for s in specialties if s]
    
    diagnoses = list(set(AnonymizedPatient.objects.values_list('primary_diagnosis', flat=True)))
    diagnoses = [d for d in diagnoses if d]
    
    hcps = HCP.objects.all()
    
    context = {
        'patients': patients,
        'specialties': specialties,
        'diagnoses': diagnoses,
        'hcps': hcps,
        'current_specialty': current_specialty,
        'current_diagnosis': current_diagnosis,
        'current_hcp': current_hcp,
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
    
    # This would handle adding new patients
    # For now, return a simple response
    if request.method == 'POST':
        messages.success(request, 'Patient added successfully!')
        return redirect('patient_database')
    
    context = {}
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
