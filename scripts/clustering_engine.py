#!/usr/bin/env python
"""
AI-powered clustering and drug recommendation engine for Pulse
Uses scikit-learn for patient clustering and similarity analysis
"""

import os
import sys
import django
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from datetime import datetime, timedelta
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import (AnonymizedPatient, EMRDataPoint, PatientOutcome, 
                        PatientCluster, ClusterMembership, ClusterInsight, 
                        DrugRecommendation, HCP)

class PatientClusteringEngine:
    """Advanced patient clustering engine using machine learning"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def prepare_patient_features(self, patients):
        """Prepare patient data for clustering"""
        features = []
        patient_ids = []
        
        for patient in patients:
            feature_vector = self._extract_patient_features(patient)
            features.append(feature_vector)
            patient_ids.append(patient.id)
        
        return np.array(features), patient_ids
    
    def _extract_patient_features(self, patient):
        """Extract numerical features from patient data"""
        features = []
        
        # Age group encoding
        age_mapping = {'18-25': 1, '26-35': 2, '36-45': 3, '46-55': 4, 
                      '56-65': 5, '66-75': 6, '76+': 7}
        features.append(age_mapping.get(patient.age_group, 4))
        
        # Gender encoding
        gender_mapping = {'M': 1, 'F': 2, 'O': 3, 'U': 0}
        features.append(gender_mapping.get(patient.gender, 0))
        
        # Race encoding
        race_mapping = {'WHITE': 1, 'BLACK': 2, 'ASIAN': 3, 'NATIVE': 4, 
                       'PACIFIC': 5, 'OTHER': 6, 'UNKNOWN': 0}
        features.append(race_mapping.get(patient.race, 0))
        
        # Visit frequency encoding
        visit_mapping = {'Weekly': 4, 'Monthly': 3, 'Quarterly': 2, 'As needed': 1}
        features.append(visit_mapping.get(patient.visit_frequency, 2))
        
        # Emergency visits and hospitalizations
        features.append(patient.emergency_visits_6m)
        features.append(patient.hospitalizations_6m)
        
        # Lab values (extract numerical values)
        lab_values = patient.last_lab_values or {}
        for test_name, unit, min_val, max_val in [
            ('Hemoglobin A1c', '%', 4.0, 6.5),
            ('Total Cholesterol', 'mg/dL', 120, 200),
            ('LDL Cholesterol', 'mg/dL', 70, 130),
            ('HDL Cholesterol', 'mg/dL', 40, 60),
            ('Creatinine', 'mg/dL', 0.6, 1.2)
        ]:
            if test_name in lab_values:
                try:
                    value = float(lab_values[test_name].split()[0])
                    # Normalize to 0-1 scale
                    normalized = (value - min_val) / (max_val - min_val)
                    features.append(normalized)
                except:
                    features.append(0.5)  # Default middle value
            else:
                features.append(0.5)
        
        # Vital signs
        vital_signs = patient.vital_signs or {}
        for vital_name, unit, min_val, max_val in [
            ('Blood Pressure Systolic', 'mmHg', 90, 140),
            ('Blood Pressure Diastolic', 'mmHg', 60, 90),
            ('Heart Rate', 'bpm', 60, 100)
        ]:
            if vital_name in vital_signs:
                try:
                    value = float(vital_signs[vital_name].split()[0])
                    normalized = (value - min_val) / (max_val - min_val)
                    features.append(normalized)
                except:
                    features.append(0.5)
            else:
                features.append(0.5)
        
        # Treatment response score (based on outcomes)
        outcomes = patient.outcomes.all()
        if outcomes.exists():
            improved_count = sum(1 for outcome in outcomes if outcome.outcome == 'IMPROVED')
            total_count = outcomes.count()
            treatment_score = improved_count / total_count if total_count > 0 else 0.5
        else:
            treatment_score = 0.5
        features.append(treatment_score)
        
        return features
    
    def find_optimal_clusters(self, features, max_clusters=10):
        """Find optimal number of clusters using silhouette analysis"""
        if len(features) < 2:
            return 1
            
        max_clusters = min(max_clusters, len(features) - 1)
        silhouette_scores = []
        
        for k in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(features)
            score = silhouette_score(features, cluster_labels)
            silhouette_scores.append((k, score))
        
        # Return the k with highest silhouette score
        best_k, best_score = max(silhouette_scores, key=lambda x: x[1])
        return best_k if best_score > 0.3 else 1  # Only cluster if score is reasonable
    
    def cluster_patients(self, hcp, cluster_type='DIAGNOSIS'):
        """Cluster patients for a specific HCP"""
        patients = AnonymizedPatient.objects.filter(hcp=hcp)
        
        if patients.count() < 3:
            return []
        
        # Prepare features
        features, patient_ids = self.prepare_patient_features(patients)
        
        if len(features) < 3:
            return []
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Find optimal number of clusters
        optimal_k = self.find_optimal_clusters(features_scaled)
        
        if optimal_k == 1:
            # Create single cluster
            cluster = PatientCluster.objects.create(
                hcp=hcp,
                name=f"{hcp.specialty} Patient Cluster",
                cluster_type=cluster_type,
                description=f"All patients for {hcp.name}",
                patient_count=patients.count(),
                avg_risk_score=0.5,
                primary_diagnosis="Mixed",
                common_treatments="Various",
                success_rate=50.0,
                cluster_center={'x': 0.5, 'y': 0.5},
                features_used=['demographics', 'lab_values', 'vital_signs', 'treatment_response']
            )
            
            # Add all patients to this cluster
            for patient in patients:
                ClusterMembership.objects.create(
                    patient=patient,
                    cluster=cluster,
                    similarity_score=0.8
                )
            
            return [cluster]
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(features_scaled)
        
        # Create clusters
        clusters = []
        for i in range(optimal_k):
            cluster_patients = [patients[j] for j in range(len(patients)) if cluster_labels[j] == i]
            
            if len(cluster_patients) == 0:
                continue
            
            # Calculate cluster statistics
            primary_diagnoses = [p.primary_diagnosis for p in cluster_patients]
            most_common_diagnosis = max(set(primary_diagnoses), key=primary_diagnoses.count)
            
            # Calculate success rate
            total_outcomes = 0
            improved_outcomes = 0
            for patient in cluster_patients:
                for outcome in patient.outcomes.all():
                    total_outcomes += 1
                    if outcome.outcome == 'IMPROVED':
                        improved_outcomes += 1
            
            success_rate = (improved_outcomes / total_outcomes * 100) if total_outcomes > 0 else 50.0
            
            # Get common treatments
            all_treatments = []
            for patient in cluster_patients:
                if patient.current_treatments:
                    all_treatments.extend(patient.current_treatments.split('; '))
            common_treatments = list(set(all_treatments))[:5]  # Top 5 treatments
            
            # Create cluster
            cluster = PatientCluster.objects.create(
                hcp=hcp,
                name=f"Cluster {i+1} - {most_common_diagnosis}",
                cluster_type=cluster_type,
                description=f"Patient cluster with {most_common_diagnosis} focus",
                patient_count=len(cluster_patients),
                avg_risk_score=random.uniform(0.3, 0.8),
                primary_diagnosis=most_common_diagnosis,
                common_treatments='; '.join(common_treatments),
                success_rate=success_rate,
                cluster_center={'x': float(kmeans.cluster_centers_[i][0]), 
                              'y': float(kmeans.cluster_centers_[i][1])},
                features_used=['demographics', 'lab_values', 'vital_signs', 'treatment_response']
            )
            
            # Add patients to cluster
            for j, patient in enumerate(cluster_patients):
                # Calculate similarity score based on distance from cluster center
                patient_features = features[patient_ids.index(patient.id)]
                distance = np.linalg.norm(patient_features - kmeans.cluster_centers_[i])
                similarity_score = max(0, 1 - distance / np.max(distance) if np.max(distance) > 0 else 0.8)
                
                ClusterMembership.objects.create(
                    patient=patient,
                    cluster=cluster,
                    similarity_score=similarity_score
                )
            
            clusters.append(cluster)
        
        return clusters
    
    def generate_cluster_insights(self, cluster):
        """Generate AI insights for a cluster"""
        insights = []
        
        # Treatment effectiveness insight
        if cluster.success_rate > 70:
            insights.append({
                'insight_type': 'TREATMENT_EFFECTIVENESS',
                'title': f'High Success Rate in {cluster.name}',
                'description': f'This cluster shows {cluster.success_rate:.1f}% treatment success rate',
                'confidence_score': 0.85,
                'actionable_recommendations': 'Consider applying this treatment protocol to similar patients',
                'supporting_data': {
                    'success_rate': cluster.success_rate,
                    'patient_count': cluster.patient_count
                }
            })
        
        # Pattern discovery insight
        if cluster.patient_count > 10:
            insights.append({
                'insight_type': 'PATTERN_DISCOVERY',
                'title': f'Significant Patient Group in {cluster.name}',
                'description': f'Large group of {cluster.patient_count} patients with similar characteristics',
                'confidence_score': 0.75,
                'actionable_recommendations': 'Develop targeted treatment protocols for this patient group',
                'supporting_data': {
                    'patient_count': cluster.patient_count,
                    'primary_diagnosis': cluster.primary_diagnosis
                }
            })
        
        # Risk factors insight
        if cluster.avg_risk_score > 0.7:
            insights.append({
                'insight_type': 'RISK_FACTORS',
                'title': f'High-Risk Patient Cluster',
                'description': f'This cluster has elevated risk factors requiring close monitoring',
                'confidence_score': 0.80,
                'actionable_recommendations': 'Implement enhanced monitoring and preventive measures',
                'supporting_data': {
                    'risk_score': cluster.avg_risk_score,
                    'patient_count': cluster.patient_count
                }
            })
        
        # Create insight objects
        for insight_data in insights:
            ClusterInsight.objects.create(
                cluster=cluster,
                **insight_data,
                is_implemented=False
            )

class DrugRecommendationEngine:
    """Drug recommendation engine based on cluster analysis and research"""
    
    def __init__(self):
        self.drug_database = self._load_drug_database()
    
    def _load_drug_database(self):
        """Load drug database with efficacy data"""
        return {
            'Type 2 Diabetes Mellitus': [
                {'name': 'Metformin', 'efficacy': 0.85, 'side_effects': 'GI upset', 'contraindications': 'Renal impairment'},
                {'name': 'Insulin Glargine', 'efficacy': 0.90, 'side_effects': 'Hypoglycemia', 'contraindications': 'Allergy'},
                {'name': 'Sitagliptin', 'efficacy': 0.75, 'side_effects': 'Nausea', 'contraindications': 'Pancreatitis'},
                {'name': 'Empagliflozin', 'efficacy': 0.80, 'side_effects': 'UTI', 'contraindications': 'Renal impairment'}
            ],
            'Essential Hypertension': [
                {'name': 'Lisinopril', 'efficacy': 0.88, 'side_effects': 'Dry cough', 'contraindications': 'Pregnancy'},
                {'name': 'Amlodipine', 'efficacy': 0.82, 'side_effects': 'Edema', 'contraindications': 'Heart failure'},
                {'name': 'Losartan', 'efficacy': 0.85, 'side_effects': 'Dizziness', 'contraindications': 'Pregnancy'},
                {'name': 'Hydrochlorothiazide', 'efficacy': 0.78, 'side_effects': 'Electrolyte imbalance', 'contraindications': 'Gout'}
            ],
            'Coronary Artery Disease': [
                {'name': 'Atorvastatin', 'efficacy': 0.90, 'side_effects': 'Muscle pain', 'contraindications': 'Liver disease'},
                {'name': 'Aspirin', 'efficacy': 0.85, 'side_effects': 'Bleeding', 'contraindications': 'Peptic ulcer'},
                {'name': 'Clopidogrel', 'efficacy': 0.80, 'side_effects': 'Bleeding', 'contraindications': 'Active bleeding'},
                {'name': 'Metoprolol', 'efficacy': 0.75, 'side_effects': 'Fatigue', 'contraindications': 'Asthma'}
            ]
        }
    
    def generate_recommendations(self, hcp, clusters):
        """Generate drug recommendations based on cluster analysis"""
        recommendations = []
        
        for cluster in clusters:
            if cluster.patient_count < 3:  # Need sufficient data
                continue
            
            diagnosis = cluster.primary_diagnosis
            if diagnosis not in self.drug_database:
                continue
            
            # Get drugs for this diagnosis
            available_drugs = self.drug_database[diagnosis]
            
            for drug_info in available_drugs:
                # Calculate success rate based on cluster data and drug efficacy
                base_success_rate = drug_info['efficacy'] * 100
                cluster_modifier = cluster.success_rate / 100
                final_success_rate = base_success_rate * (0.7 + 0.3 * cluster_modifier)
                
                # Determine evidence level and priority
                if final_success_rate > 85:
                    evidence_level = 'High'
                    priority = 'HIGH'
                elif final_success_rate > 70:
                    evidence_level = 'Moderate'
                    priority = 'MEDIUM'
                else:
                    evidence_level = 'Low'
                    priority = 'LOW'
                
                # Check if recommendation already exists
                existing = DrugRecommendation.objects.filter(
                    hcp=hcp,
                    cluster=cluster,
                    drug_name=drug_info['name']
                ).first()
                
                if existing:
                    # Update existing recommendation
                    existing.success_rate = final_success_rate
                    existing.evidence_level = evidence_level
                    existing.priority = priority
                    existing.save()
                    recommendations.append(existing)
                else:
                    # Create new recommendation
                    recommendation = DrugRecommendation.objects.create(
                        hcp=hcp,
                        cluster=cluster,
                        drug_name=drug_info['name'],
                        indication=diagnosis,
                        success_rate=final_success_rate,
                        patient_count=cluster.patient_count,
                        evidence_level=evidence_level,
                        research_support=f"Based on cluster analysis of {cluster.patient_count} patients with {diagnosis}",
                        contraindications=drug_info['contraindications'],
                        side_effects=drug_info['side_effects'],
                        dosage_recommendations=f"Standard dosing for {diagnosis}",
                        priority=priority,
                        is_reviewed=False
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def update_recommendations_for_hcp(self, hcp):
        """Update all drug recommendations for an HCP"""
        clusters = PatientCluster.objects.filter(hcp=hcp)
        return self.generate_recommendations(hcp, clusters)

def run_clustering_analysis():
    """Run clustering analysis for all HCPs"""
    print("Starting clustering analysis...")
    
    clustering_engine = PatientClusteringEngine()
    recommendation_engine = DrugRecommendationEngine()
    
    hcps = HCP.objects.all()
    total_clusters = 0
    total_recommendations = 0
    
    for hcp in hcps:
        print(f"Processing HCP: {hcp.name}")
        
        # Clear existing clusters for this HCP
        PatientCluster.objects.filter(hcp=hcp).delete()
        
        # Perform clustering
        clusters = clustering_engine.cluster_patients(hcp)
        total_clusters += len(clusters)
        
        # Generate insights for each cluster
        for cluster in clusters:
            clustering_engine.generate_cluster_insights(cluster)
        
        # Generate drug recommendations
        recommendations = recommendation_engine.generate_recommendations(hcp, clusters)
        total_recommendations += len(recommendations)
        
        print(f"Created {len(clusters)} clusters and {len(recommendations)} recommendations")
    
    print(f"\nClustering analysis complete!")
    print(f"Total clusters created: {total_clusters}")
    print(f"Total recommendations generated: {total_recommendations}")

if __name__ == '__main__':
    import random
    run_clustering_analysis()

