from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
import json

from .models import PatientCluster, DrugRecommendation, ClusterInsight
from .views import generate_cluster_based_recommendations, cohort_cluster_network

@require_http_methods(["GET"])
def cluster_network_data(request):
    """API endpoint to get cluster network data"""
    try:
        # Get the same data as the cohort_cluster_network view
        from .views import cohort_cluster_network
        from django.test import RequestFactory
        
        # Create a mock request
        factory = RequestFactory()
        mock_request = factory.get('/api/cluster-network-data/')
        mock_request.user = request.user
        
        # Get the context from the view
        context = cohort_cluster_network(mock_request)
        
        # Extract nodes and links from context
        nodes = json.loads(context['nodes']) if 'nodes' in context else []
        links = json.loads(context['links']) if 'links' in context else []
        
        return JsonResponse({
            'nodes': nodes,
            'links': links,
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

@require_http_methods(["GET"])
def cluster_recommendations(request, cluster_id):
    """API endpoint to get treatment recommendations for a specific cluster"""
    try:
        cluster = get_object_or_404(PatientCluster, id=cluster_id)
        
        # Generate cluster-based recommendations
        recommendations = generate_cluster_based_recommendations(cluster)
        
        # Convert to JSON-serializable format
        json_recommendations = []
        for rec in recommendations:
            json_rec = {
                'cluster_id': rec['cluster_id'],
                'cluster_name': rec['cluster_name'],
                'drug_name': rec['drug_name'],
                'indication': rec['indication'],
                'success_rate': rec['success_rate'],
                'patient_count': rec['patient_count'],
                'evidence_level': rec['evidence_level'],
                'priority': rec['priority'],
                'research_support': rec['research_support'],
                'hcp': {
                    'id': rec['hcp'].id,
                    'name': rec['hcp'].name,
                    'specialty': rec['hcp'].specialty
                }
            }
            json_recommendations.append(json_rec)
        
        return JsonResponse({
            'recommendations': json_recommendations,
            'cluster': {
                'id': cluster.id,
                'name': cluster.name,
                'patient_count': cluster.patient_count,
                'success_rate': cluster.success_rate,
                'primary_diagnosis': cluster.primary_diagnosis
            },
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

@require_http_methods(["GET"])
def cluster_evidence(request, cluster_id):
    """API endpoint to get detailed evidence for a cluster"""
    try:
        cluster = get_object_or_404(PatientCluster, id=cluster_id)
        
        # Get cluster patients and their outcomes
        cluster_patients = []
        for membership in cluster.patients.all():
            patient = membership.patient
            patient_outcomes = list(patient.outcomes.all())
            cluster_patients.append({
                'patient': patient,
                'outcomes': patient_outcomes,
                'success_rate': calculate_patient_success_rate(patient_outcomes)
            })
        
        # Analyze treatment success patterns
        treatment_success = {}
        for patient_data in cluster_patients:
            for outcome in patient_data['outcomes']:
                treatment = outcome.treatment
                if treatment not in treatment_success:
                    treatment_success[treatment] = {
                        'total_patients': 0,
                        'successful_patients': 0,
                        'success_rates': [],
                        'patient_demographics': [],
                        'comorbidities': set(),
                        'diagnoses': set()
                    }
                
                treatment_success[treatment]['total_patients'] += 1
                if patient_data['success_rate'] > 70:
                    treatment_success[treatment]['successful_patients'] += 1
                
                treatment_success[treatment]['success_rates'].append(patient_data['success_rate'])
                treatment_success[treatment]['patient_demographics'].append({
                    'age_group': patient_data['patient'].age_group,
                    'gender': patient_data['patient'].gender,
                    'race': patient_data['patient'].race
                })
                
                if patient_data['patient'].comorbidities:
                    treatment_success[treatment]['comorbidities'].update(
                        patient_data['patient'].comorbidities.split(',')
                    )
                if patient_data['patient'].primary_diagnosis:
                    treatment_success[treatment]['diagnoses'].add(patient_data['patient'].primary_diagnosis)
        
        # Calculate overall statistics
        total_patients = len(cluster_patients)
        avg_success_rate = sum(p['success_rate'] for p in cluster_patients) / total_patients if total_patients > 0 else 0
        
        # Get demographics
        demographics = []
        for patient_data in cluster_patients:
            demographics.append({
                'age_group': patient_data['patient'].age_group,
                'gender': patient_data['patient'].gender,
                'race': patient_data['patient'].race
            })
        
        # Get all comorbidities
        all_comorbidities = set()
        for patient_data in cluster_patients:
            if patient_data['patient'].comorbidities:
                all_comorbidities.update(patient_data['patient'].comorbidities.split(','))
        
        # Format treatment data
        treatments = []
        for treatment, data in treatment_success.items():
            if data['total_patients'] >= 3:  # Only include treatments with sufficient evidence
                cluster_success_rate = (data['successful_patients'] / data['total_patients']) * 100
                avg_treatment_success = sum(data['success_rates']) / len(data['success_rates'])
                
                # Determine evidence level
                if data['total_patients'] >= 10 and cluster_success_rate >= 80:
                    evidence_level = 'High'
                elif data['total_patients'] >= 5 and cluster_success_rate >= 70:
                    evidence_level = 'Moderate'
                else:
                    evidence_level = 'Low'
                
                treatments.append({
                    'name': treatment,
                    'success_rate': round(cluster_success_rate, 1),
                    'patient_count': data['total_patients'],
                    'evidence_level': evidence_level,
                    'comorbidities': list(data['comorbidities']),
                    'diagnoses': list(data['diagnoses'])
                })
        
        # Sort treatments by success rate
        treatments.sort(key=lambda x: x['success_rate'], reverse=True)
        
        return JsonResponse({
            'cluster': {
                'id': cluster.id,
                'name': cluster.name,
                'patient_count': cluster.patient_count,
                'success_rate': cluster.success_rate,
                'primary_diagnosis': cluster.primary_diagnosis
            },
            'total_patients': total_patients,
            'avg_success_rate': round(avg_success_rate, 1),
            'demographics': demographics,
            'comorbidities': list(all_comorbidities),
            'treatments': treatments,
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def calculate_patient_success_rate(outcomes):
    """Calculate success rate for a patient based on their outcomes"""
    if not outcomes:
        return 0
    
    # Simple success detection based on outcome keywords
    success_keywords = ['success', 'effective', 'improved', 'positive', 'recovery', 'stable']
    success_count = 0
    
    for outcome in outcomes:
        outcome_text = outcome.treatment.lower()
        if any(keyword in outcome_text for keyword in success_keywords):
            success_count += 1
    
    return (success_count / len(outcomes)) * 100
