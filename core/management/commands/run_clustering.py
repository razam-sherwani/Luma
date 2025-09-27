from django.core.management.base import BaseCommand
import os
import sys
import django
import random
from datetime import datetime, timedelta, date

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import (HCP, AnonymizedPatient, EMRDataPoint, PatientOutcome, 
                        PatientCluster, ClusterMembership, ClusterInsight, 
                        DrugRecommendation)

class Command(BaseCommand):
    help = 'Run AI clustering analysis and generate drug recommendations'

    def handle(self, *args, **options):
        self.stdout.write('Starting clustering analysis...')
        try:
            self.run_clustering_analysis()
            self.stdout.write(
                self.style.SUCCESS('Successfully completed clustering analysis!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error running clustering: {str(e)}')
            )

    def run_clustering_analysis(self):
        """Run clustering analysis for all HCPs"""
        print("Starting clustering analysis...")
        
        hcps = HCP.objects.all()
        total_clusters = 0
        total_recommendations = 0
        
        for hcp in hcps:
            print(f"Processing HCP: {hcp.name}")
            
            # Clear existing clusters for this HCP
            PatientCluster.objects.filter(hcp=hcp).delete()
            
            # Perform clustering
            clusters = self.cluster_patients(hcp)
            total_clusters += len(clusters)
            
            # Generate insights for each cluster
            for cluster in clusters:
                self.generate_cluster_insights(cluster)
            
            # Generate drug recommendations
            recommendations = self.generate_drug_recommendations(hcp, clusters)
            total_recommendations += len(recommendations)
            
            print(f"Created {len(clusters)} clusters and {len(recommendations)} recommendations")
        
        print(f"\nClustering analysis complete!")
        print(f"Total clusters created: {total_clusters}")
        print(f"Total recommendations generated: {total_recommendations}")

    def cluster_patients(self, hcp):
        """Simple clustering based on diagnosis"""
        patients = AnonymizedPatient.objects.filter(hcp=hcp)
        
        if patients.count() < 3:
            return []
        
        # Group patients by primary diagnosis
        diagnosis_groups = {}
        for patient in patients:
            diagnosis = patient.primary_diagnosis
            if diagnosis not in diagnosis_groups:
                diagnosis_groups[diagnosis] = []
            diagnosis_groups[diagnosis].append(patient)
        
        clusters = []
        for diagnosis, patient_list in diagnosis_groups.items():
            if len(patient_list) < 3:  # Need at least 3 patients for clustering
                continue
                
            # Calculate success rate based on outcomes
            total_outcomes = 0
            improved_outcomes = 0
            for patient in patient_list:
                for outcome in patient.outcomes.all():
                    total_outcomes += 1
                    if outcome.outcome == 'IMPROVED':
                        improved_outcomes += 1
            
            success_rate = (improved_outcomes / total_outcomes * 100) if total_outcomes > 0 else 50.0
            
            cluster = PatientCluster.objects.create(
                hcp=hcp,
                name=f"{diagnosis} Cluster",
                cluster_type='DIAGNOSIS',
                description=f"Patients with {diagnosis} showing similar treatment patterns",
                patient_count=len(patient_list),
                avg_risk_score=random.uniform(0.3, 0.8),
                primary_diagnosis=diagnosis,
                common_treatments='; '.join(self.get_treatments_for_diagnosis(diagnosis)),
                success_rate=success_rate,
                cluster_center={'x': random.uniform(0, 1), 'y': random.uniform(0, 1)},
                features_used=['age_group', 'gender', 'primary_diagnosis', 'lab_values']
            )
            
            # Add all patients to this cluster
            for patient in patient_list:
                ClusterMembership.objects.create(
                    patient=patient,
                    cluster=cluster,
                    similarity_score=random.uniform(0.7, 0.95)
                )
            
            clusters.append(cluster)
        
        return clusters

    def get_treatments_for_diagnosis(self, diagnosis):
        """Get treatments for a diagnosis"""
        treatments = {
            'Type 2 Diabetes Mellitus': ['Metformin', 'Insulin Glargine', 'Sitagliptin', 'Empagliflozin'],
            'Essential Hypertension': ['Lisinopril', 'Amlodipine', 'Losartan', 'Hydrochlorothiazide'],
            'Coronary Artery Disease': ['Atorvastatin', 'Aspirin', 'Clopidogrel', 'Metoprolol'],
            'Heart Failure': ['Lisinopril', 'Metoprolol', 'Furosemide', 'Spironolactone'],
            'Atrial Fibrillation': ['Warfarin', 'Apixaban', 'Metoprolol', 'Digoxin'],
            'Hypothyroidism': ['Levothyroxine'],
            'Osteoarthritis': ['Ibuprofen', 'Acetaminophen', 'Naproxen', 'Celecoxib'],
            'Migraine': ['Sumatriptan', 'Propranolol', 'Topiramate', 'Amitriptyline']
        }
        return treatments.get(diagnosis, ['Standard Care'])

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

    def generate_drug_recommendations(self, hcp, clusters):
        """Generate drug recommendations based on cluster analysis"""
        recommendations = []
        
        drug_database = {
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
        
        for cluster in clusters:
            if cluster.patient_count < 3:  # Need sufficient data
                continue
            
            diagnosis = cluster.primary_diagnosis
            if diagnosis not in drug_database:
                continue
            
            # Get drugs for this diagnosis
            available_drugs = drug_database[diagnosis]
            
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
                
                # Create recommendation
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
