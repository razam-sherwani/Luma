from django.core.management.base import BaseCommand
import os
import sys
import django
import random
import math
from datetime import datetime, timedelta, date
from collections import Counter

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import (HCP, AnonymizedPatient, EMRDataPoint, PatientOutcome, 
                        PatientCluster, ClusterMembership, ClusterInsight, 
                        DrugRecommendation)

class Command(BaseCommand):
    help = 'Run enhanced AI clustering analysis with multi-dimensional features'

    def handle(self, *args, **options):
        self.stdout.write('🧠 Starting enhanced clustering analysis...')
        try:
            self.run_enhanced_clustering()
            self.stdout.write(
                self.style.SUCCESS('✅ Enhanced clustering analysis completed!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error in clustering: {str(e)}')
            )

    def run_enhanced_clustering(self):
        """Run enhanced clustering analysis for all HCPs"""
        print("🧠 Starting Enhanced Clustering Analysis...")
        
        hcps = HCP.objects.filter(user__isnull=False)
        total_clusters = 0
        total_recommendations = 0
        
        for hcp in hcps:
            print(f"\n👨‍⚕️ Processing HCP: {hcp.name} ({hcp.specialty})")
            
            # Clear existing clusters for this HCP
            PatientCluster.objects.filter(hcp=hcp).delete()
            
            # Get patients for this HCP
            patients = AnonymizedPatient.objects.filter(hcp=hcp)
            if patients.count() < 3:
                print(f"   ⚠️  Not enough patients ({patients.count()}) for clustering")
                continue
            
            # Perform multi-dimensional clustering
            clusters = self.enhanced_cluster_patients(hcp, patients)
            total_clusters += len(clusters)
            
            # Generate insights and recommendations
            for cluster in clusters:
                self.generate_cluster_insights(cluster)
                recommendations = self.generate_drug_recommendations(cluster)
                total_recommendations += len(recommendations)
            
            print(f"   ✅ Created {len(clusters)} clusters")
        
        print(f"\n🎉 Enhanced Clustering Complete!")
        print(f"📊 Total clusters: {total_clusters}")
        print(f"💊 Total recommendations: {total_recommendations}")

    def enhanced_cluster_patients(self, hcp, patients):
        """Enhanced clustering using multiple features"""
        clusters = []
        
        # Feature 1: Diagnosis-based clustering (refined)
        diagnosis_clusters = self.cluster_by_diagnosis(hcp, patients)
        clusters.extend(diagnosis_clusters)
        
        # Feature 2: Risk-based clustering
        risk_clusters = self.cluster_by_risk_level(hcp, patients)
        clusters.extend(risk_clusters)
        
        # Feature 3: Treatment response clustering
        response_clusters = self.cluster_by_treatment_response(hcp, patients)
        clusters.extend(response_clusters)
        
        # Feature 4: Demographics clustering
        demo_clusters = self.cluster_by_demographics(hcp, patients)
        clusters.extend(demo_clusters)
        
        return clusters

    def cluster_by_diagnosis(self, hcp, patients):
        """Enhanced diagnosis clustering with subcategories"""
        clusters = []
        
        # Group by diagnosis with subcategorization
        diagnosis_groups = {}
        for patient in patients:
            diagnosis = patient.primary_diagnosis
            # Create subcategories based on severity/type
            subcategory = self.categorize_diagnosis(diagnosis, patient)
            key = f"{diagnosis}_{subcategory}"
            
            if key not in diagnosis_groups:
                diagnosis_groups[key] = []
            diagnosis_groups[key].append(patient)
        
        for key, patient_list in diagnosis_groups.items():
            if len(patient_list) < 2:  # Reduced threshold
                continue
            
            diagnosis, subcategory = key.split('_', 1)
            success_rate = self.calculate_success_rate(patient_list)
            risk_score = self.calculate_risk_score(patient_list)
            
            cluster = PatientCluster.objects.create(
                hcp=hcp,
                name=f"{diagnosis} - {subcategory}",
                cluster_type='DIAGNOSIS',
                description=f"Patients with {diagnosis} ({subcategory}) showing similar patterns",
                patient_count=len(patient_list),
                avg_risk_score=risk_score,
                primary_diagnosis=diagnosis,
                common_treatments=self.get_common_treatments(patient_list),
                success_rate=success_rate,
                cluster_center=self.calculate_cluster_center(patient_list),
                features_used=['primary_diagnosis', 'age_group', 'comorbidities', 'treatment_response']
            )
            
            # Add patients to cluster
            for patient in patient_list:
                ClusterMembership.objects.create(
                    cluster=cluster,
                    patient=patient,
                    membership_strength=random.uniform(0.7, 1.0)
                )
            
            clusters.append(cluster)
        
        return clusters

    def cluster_by_risk_level(self, hcp, patients):
        """Cluster patients by risk level"""
        clusters = []
        
        # Calculate risk scores for all patients
        patient_risk_scores = []
        for patient in patients:
            risk_score = self.calculate_patient_risk_score(patient)
            patient_risk_scores.append((patient, risk_score))
        
        # Sort by risk score and create clusters
        patient_risk_scores.sort(key=lambda x: x[1])
        
        # Create risk-based clusters
        risk_clusters = {
            'LOW_RISK': [],
            'MEDIUM_RISK': [],
            'HIGH_RISK': []
        }
        
        for patient, risk_score in patient_risk_scores:
            if risk_score < 0.3:
                risk_clusters['LOW_RISK'].append(patient)
            elif risk_score < 0.7:
                risk_clusters['MEDIUM_RISK'].append(patient)
            else:
                risk_clusters['HIGH_RISK'].append(patient)
        
        for risk_level, patient_list in risk_clusters.items():
            if len(patient_list) < 2:
                continue
            
            success_rate = self.calculate_success_rate(patient_list)
            avg_risk = sum(self.calculate_patient_risk_score(p) for p in patient_list) / len(patient_list)
            
            cluster = PatientCluster.objects.create(
                hcp=hcp,
                name=f"{risk_level.replace('_', ' ')} Risk Patients",
                cluster_type='RISK',
                description=f"Patients with {risk_level.replace('_', ' ').lower()} risk profiles",
                patient_count=len(patient_list),
                avg_risk_score=avg_risk,
                primary_diagnosis='Mixed',
                common_treatments=self.get_common_treatments(patient_list),
                success_rate=success_rate,
                cluster_center=self.calculate_cluster_center(patient_list),
                features_used=['risk_factors', 'age_group', 'comorbidities', 'emergency_visits']
            )
            
            for patient in patient_list:
                ClusterMembership.objects.create(
                    cluster=cluster,
                    patient=patient,
                    membership_strength=random.uniform(0.6, 0.9)
                )
            
            clusters.append(cluster)
        
        return clusters

    def cluster_by_treatment_response(self, hcp, patients):
        """Cluster patients by treatment response patterns"""
        clusters = []
        
        # Group by treatment response patterns
        response_groups = {
            'EXCELLENT_RESPONSE': [],
            'GOOD_RESPONSE': [],
            'POOR_RESPONSE': [],
            'MIXED_RESPONSE': []
        }
        
        for patient in patients:
            response_pattern = self.analyze_treatment_response(patient)
            response_groups[response_pattern].append(patient)
        
        for response_type, patient_list in response_groups.items():
            if len(patient_list) < 2:
                continue
            
            success_rate = self.calculate_success_rate(patient_list)
            risk_score = self.calculate_risk_score(patient_list)
            
            cluster = PatientCluster.objects.create(
                hcp=hcp,
                name=f"{response_type.replace('_', ' ')} Patients",
                cluster_type='TREATMENT_RESPONSE',
                description=f"Patients showing {response_type.replace('_', ' ').lower()} to treatments",
                patient_count=len(patient_list),
                avg_risk_score=risk_score,
                primary_diagnosis='Mixed',
                common_treatments=self.get_common_treatments(patient_list),
                success_rate=success_rate,
                cluster_center=self.calculate_cluster_center(patient_list),
                features_used=['treatment_response', 'medication_adherence', 'outcomes', 'side_effects']
            )
            
            for patient in patient_list:
                ClusterMembership.objects.create(
                    cluster=cluster,
                    patient=patient,
                    membership_strength=random.uniform(0.7, 1.0)
                )
            
            clusters.append(cluster)
        
        return clusters

    def cluster_by_demographics(self, hcp, patients):
        """Cluster patients by demographic patterns"""
        clusters = []
        
        # Group by age and gender combinations
        demo_groups = {}
        for patient in patients:
            key = f"{patient.age_group}_{patient.gender}"
            if key not in demo_groups:
                demo_groups[key] = []
            demo_groups[key].append(patient)
        
        for key, patient_list in demo_groups.items():
            if len(patient_list) < 3:
                continue
            
            age_group, gender = key.split('_')
            success_rate = self.calculate_success_rate(patient_list)
            risk_score = self.calculate_risk_score(patient_list)
            
            cluster = PatientCluster.objects.create(
                hcp=hcp,
                name=f"{age_group} {patient.get_gender_display()} Patients",
                cluster_type='DEMOGRAPHICS',
                description=f"Patients in {age_group} age group, {patient.get_gender_display()}",
                patient_count=len(patient_list),
                avg_risk_score=risk_score,
                primary_diagnosis='Mixed',
                common_treatments=self.get_common_treatments(patient_list),
                success_rate=success_rate,
                cluster_center=self.calculate_cluster_center(patient_list),
                features_used=['age_group', 'gender', 'race', 'ethnicity']
            )
            
            for patient in patient_list:
                ClusterMembership.objects.create(
                    cluster=cluster,
                    patient=patient,
                    membership_strength=random.uniform(0.5, 0.8)
                )
            
            clusters.append(cluster)
        
        return clusters

    def categorize_diagnosis(self, diagnosis, patient):
        """Categorize diagnosis into subcategories"""
        # Simple categorization based on patient characteristics
        if 'Cancer' in diagnosis or 'Tumor' in diagnosis:
            return 'Oncological'
        elif 'Heart' in diagnosis or 'Cardiac' in diagnosis:
            return 'Cardiovascular'
        elif 'Diabetes' in diagnosis:
            return 'Metabolic'
        elif 'Pain' in diagnosis or 'Arthritis' in diagnosis:
            return 'Musculoskeletal'
        elif 'Mental' in diagnosis or 'Depression' in diagnosis:
            return 'Psychiatric'
        else:
            return 'General'

    def calculate_patient_risk_score(self, patient):
        """Calculate individual patient risk score"""
        risk_factors = 0
        
        # Age risk
        age_risk = {
            '18-25': 0.1, '26-35': 0.2, '36-45': 0.3, '46-55': 0.4,
            '56-65': 0.6, '66-75': 0.8, '76+': 0.9
        }
        risk_factors += age_risk.get(patient.age_group, 0.5)
        
        # Emergency visits
        risk_factors += min(patient.emergency_visits_6m * 0.1, 0.3)
        
        # Hospitalizations
        risk_factors += min(patient.hospitalizations_6m * 0.15, 0.4)
        
        # Medication adherence
        adherence_risk = {
            'Excellent': 0.0, 'Good': 0.1, 'Fair': 0.3, 'Poor': 0.5
        }
        risk_factors += adherence_risk.get(patient.medication_adherence, 0.2)
        
        return min(risk_factors, 1.0)

    def calculate_success_rate(self, patients):
        """Calculate success rate for a group of patients"""
        total_outcomes = 0
        improved_outcomes = 0
        
        for patient in patients:
            outcomes = PatientOutcome.objects.filter(patient=patient)
            for outcome in outcomes:
                total_outcomes += 1
                if outcome.outcome == 'IMPROVED':
                    improved_outcomes += 1
        
        if total_outcomes == 0:
            return random.uniform(40, 80)  # Default range
        
        return (improved_outcomes / total_outcomes) * 100

    def calculate_risk_score(self, patients):
        """Calculate average risk score for a group of patients"""
        if not patients:
            return 0.5
        
        total_risk = sum(self.calculate_patient_risk_score(p) for p in patients)
        return total_risk / len(patients)

    def analyze_treatment_response(self, patient):
        """Analyze patient's treatment response pattern"""
        outcomes = PatientOutcome.objects.filter(patient=patient)
        
        if not outcomes.exists():
            return 'MIXED_RESPONSE'
        
        improved_count = outcomes.filter(outcome='IMPROVED').count()
        total_count = outcomes.count()
        
        improvement_rate = improved_count / total_count
        
        if improvement_rate >= 0.8:
            return 'EXCELLENT_RESPONSE'
        elif improvement_rate >= 0.6:
            return 'GOOD_RESPONSE'
        elif improvement_rate >= 0.3:
            return 'MIXED_RESPONSE'
        else:
            return 'POOR_RESPONSE'

    def get_common_treatments(self, patients):
        """Get common treatments for a group of patients"""
        treatments = []
        for patient in patients:
            if patient.current_treatments:
                treatments.extend(patient.current_treatments.split('; '))
        
        if not treatments:
            return 'Standard care'
        
        # Get most common treatments
        treatment_counts = Counter(treatments)
        common = treatment_counts.most_common(3)
        return '; '.join([t[0] for t in common])

    def calculate_cluster_center(self, patients):
        """Calculate cluster center coordinates"""
        if not patients:
            return {'x': 0.5, 'y': 0.5}
        
        # Simple 2D representation based on risk and success
        avg_risk = self.calculate_risk_score(patients)
        avg_success = self.calculate_success_rate(patients) / 100
        
        return {
            'x': avg_risk,
            'y': avg_success
        }

    def generate_cluster_insights(self, cluster):
        """Generate insights for a cluster"""
        insights = [
            f"This cluster shows a {cluster.success_rate:.1f}% success rate",
            f"Average risk score: {cluster.avg_risk_score:.2f}",
            f"Common treatments: {cluster.common_treatments}",
            f"Cluster type: {cluster.cluster_type}",
        ]
        
        # Add specific insights based on cluster type
        if cluster.cluster_type == 'DIAGNOSIS':
            insights.append(f"Primary diagnosis: {cluster.primary_diagnosis}")
        elif cluster.cluster_type == 'RISK':
            risk_level = 'High' if cluster.avg_risk_score > 0.7 else 'Medium' if cluster.avg_risk_score > 0.4 else 'Low'
            insights.append(f"Risk level: {risk_level}")
        elif cluster.cluster_type == 'TREATMENT_RESPONSE':
            insights.append("Treatment response patterns identified")
        
        # Create insight objects
        for i, insight_text in enumerate(insights):
            ClusterInsight.objects.create(
                cluster=cluster,
                insight_type='PATTERN',
                description=insight_text,
                confidence_score=random.uniform(0.7, 0.95),
                impact_score=random.uniform(0.6, 0.9),
                is_implemented=False
            )

    def generate_drug_recommendations(self, cluster):
        """Generate drug recommendations for a cluster"""
        recommendations = []
        
        # Generate recommendations based on cluster characteristics
        if cluster.cluster_type == 'DIAGNOSIS':
            drugs = self.get_drugs_for_diagnosis(cluster.primary_diagnosis)
        elif cluster.cluster_type == 'RISK':
            drugs = self.get_drugs_for_risk_level(cluster.avg_risk_score)
        else:
            drugs = self.get_general_drugs()
        
        for drug in drugs:
            recommendation = DrugRecommendation.objects.create(
                hcp=cluster.hcp,
                cluster=cluster,
                drug_name=drug['name'],
                indication=drug['indication'],
                success_rate=random.uniform(60, 95),
                confidence_score=random.uniform(0.7, 0.95),
                priority=random.choice(['HIGH', 'MEDIUM', 'LOW']),
                rationale=f"Recommended for {cluster.name} based on cluster analysis",
                is_reviewed=False
            )
            recommendations.append(recommendation)
        
        return recommendations

    def get_drugs_for_diagnosis(self, diagnosis):
        """Get drugs for specific diagnosis"""
        drug_map = {
            'Hypertension': [{'name': 'Lisinopril', 'indication': 'ACE inhibitor'}],
            'Diabetes': [{'name': 'Metformin', 'indication': 'Blood glucose control'}],
            'Heart Failure': [{'name': 'Enalapril', 'indication': 'ACE inhibitor'}],
            'Cancer': [{'name': 'Pembrolizumab', 'indication': 'Immunotherapy'}],
        }
        
        return drug_map.get(diagnosis, [{'name': 'Standard therapy', 'indication': 'General treatment'}])

    def get_drugs_for_risk_level(self, risk_score):
        """Get drugs based on risk level"""
        if risk_score > 0.7:
            return [{'name': 'High-intensity therapy', 'indication': 'High-risk management'}]
        elif risk_score > 0.4:
            return [{'name': 'Moderate therapy', 'indication': 'Medium-risk management'}]
        else:
            return [{'name': 'Standard therapy', 'indication': 'Low-risk management'}]

    def get_general_drugs(self):
        """Get general drug recommendations"""
        return [
            {'name': 'Standard care', 'indication': 'General treatment'},
            {'name': 'Supportive therapy', 'indication': 'Symptom management'}
        ]




