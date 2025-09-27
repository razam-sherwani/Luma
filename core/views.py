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
    
    # Get all clusters with their patients and treatments
    clusters = PatientCluster.objects.select_related('hcp').prefetch_related('patients__patient__outcomes', 'patients__patient__data_points')
    
    # Apply specialty filter
    if current_specialty:
        clusters = clusters.filter(hcp__specialty=current_specialty)
    
    # Get unique values for filter dropdowns
    specialties = list(set(PatientCluster.objects.values_list('hcp__specialty', flat=True)))
    specialties = [s for s in specialties if s]  # Remove None values
    
    # Get all unique treatments and diagnoses
    all_treatments = set()
    all_diagnoses = set()
    for cluster in clusters:
        for patient in cluster.patients.all():
            for outcome in patient.outcomes.all():
                all_treatments.add(outcome.treatment_name)
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
        
        for patient in cluster.patients.all():
            for outcome in patient.outcomes.all():
                cluster_treatment_list.append(outcome.treatment_name)
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
        
        # Calculate risk level
        if cluster.patient_count > 40:
            risk_level = 'high'
        elif cluster.patient_count > 20:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Apply risk filter
        if current_risk and risk_level != current_risk:
            continue
        
        # Store treatments for similarity calculation
        cluster_treatments[cluster.id] = set(cluster_treatment_list)
        
        nodes.append({
            'id': f"cluster_{cluster.id}",
            'name': cluster.name,
            'type': 'cluster',
            'patient_count': cluster.patient_count,
            'success_rate': round(success_rate, 1),
            'risk_level': risk_level,
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
    
    for i, cluster1_id in enumerate(cluster_ids):
        for cluster2_id in cluster_ids[i+1:]:
            treatments1 = cluster_treatments[cluster1_id]
            treatments2 = cluster_treatments[cluster2_id]
            
            # Calculate Jaccard similarity (intersection over union)
            intersection = len(treatments1.intersection(treatments2))
            union = len(treatments1.union(treatments2))
            similarity = intersection / union if union > 0 else 0
            
            # Only create links for clusters with significant treatment overlap (>20%)
            if similarity > 0.2:
                # Determine link strength and color based on similarity
                if similarity > 0.7:
                    link_strength = 'strong'
                    link_color = '#e74c3c'  # Red for high similarity
                elif similarity > 0.4:
                    link_strength = 'medium'
                    link_color = '#f39c12'  # Orange for medium similarity
                else:
                    link_strength = 'weak'
                    link_color = '#27ae60'  # Green for low similarity
                
                links.append({
                    'source': f"cluster_{cluster1_id}",
                    'target': f"cluster_{cluster2_id}",
                    'similarity': round(similarity * 100, 1),
                    'strength': link_strength,
                    'color': link_color,
                    'shared_treatments': list(treatments1.intersection(treatments2))
                })
    
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

def calculate_risk_similarity(node1, node2):
    """Calculate risk factor similarity between two nodes"""
    risk_scores = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
    
    score1 = risk_scores.get(node1['risk_level'], 0.5)
    score2 = risk_scores.get(node2['risk_level'], 0.5)
    
    # Calculate similarity as inverse of difference
    difference = abs(score1 - score2)
    similarity = (1 - difference) * 100
    
    return similarity

def get_risk_score(risk_level):
    """Convert risk level to numeric score"""
    risk_scores = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
    return risk_scores.get(risk_level, 0.5)

def generate_intervention_recommendation(node1, node2, similarity):
    """Generate recommended intervention based on node similarity"""
    if similarity > 0.7:
        return f"High similarity detected - consider unified treatment protocols for both {node1['name']} and {node2['name']}"
    elif similarity > 0.5:
        return f"Moderate similarity - evaluate cross-cohort treatment strategies between {node1['name']} and {node2['name']}"
    else:
        return f"Low similarity - monitor for potential treatment pattern convergence between {node1['name']} and {node2['name']}"
