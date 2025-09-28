#!/usr/bin/env python
"""
Comprehensive patient EMR data seeder for Pulse
Creates realistic patient data with EMR records for each HCP
"""

import os
import sys
import django
import random
import json
from datetime import datetime, timedelta, date
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import (HCP, AnonymizedPatient, EMRDataPoint, PatientOutcome, 
                        PatientCluster, ClusterMembership, ClusterInsight, 
                        DrugRecommendation, UserProfile)

# Medical data for realistic generation
DIAGNOSES = {
    'INTERNAL MEDICINE': [
        'Type 2 Diabetes Mellitus', 'Essential Hypertension', 'Hyperlipidemia',
        'Coronary Artery Disease', 'Atrial Fibrillation', 'Heart Failure',
        'Chronic Kidney Disease', 'Hypothyroidism', 'Osteoarthritis',
        'Gastroesophageal Reflux Disease', 'Irritable Bowel Syndrome'
    ],
    'CARDIOLOGY': [
        'Coronary Artery Disease', 'Atrial Fibrillation', 'Heart Failure',
        'Hypertensive Heart Disease', 'Aortic Stenosis', 'Mitral Regurgitation',
        'Peripheral Artery Disease', 'Deep Vein Thrombosis', 'Pulmonary Embolism'
    ],
    'ENDOCRINOLOGY': [
        'Type 1 Diabetes Mellitus', 'Type 2 Diabetes Mellitus', 'Hypothyroidism',
        'Hyperthyroidism', 'Adrenal Insufficiency', 'Cushing Syndrome',
        'Osteoporosis', 'Metabolic Syndrome', 'Polycystic Ovary Syndrome'
    ],
    'NEUROLOGY': [
        'Migraine', 'Epilepsy', 'Parkinson Disease', 'Multiple Sclerosis',
        'Alzheimer Disease', 'Stroke', 'Peripheral Neuropathy', 'Seizure Disorder'
    ],
    'ONCOLOGY': [
        'Breast Cancer', 'Lung Cancer', 'Colorectal Cancer', 'Prostate Cancer',
        'Lymphoma', 'Leukemia', 'Melanoma', 'Pancreatic Cancer'
    ]
}

TREATMENTS = {
    'Type 2 Diabetes Mellitus': ['Metformin', 'Insulin Glargine', 'Sitagliptin', 'Empagliflozin'],
    'Essential Hypertension': ['Lisinopril', 'Amlodipine', 'Losartan', 'Hydrochlorothiazide'],
    'Coronary Artery Disease': ['Atorvastatin', 'Aspirin', 'Clopidogrel', 'Metoprolol'],
    'Heart Failure': ['Lisinopril', 'Metoprolol', 'Furosemide', 'Spironolactone'],
    'Atrial Fibrillation': ['Warfarin', 'Apixaban', 'Metoprolol', 'Digoxin'],
    'Hypothyroidism': ['Levothyroxine'],
    'Osteoarthritis': ['Ibuprofen', 'Acetaminophen', 'Naproxen', 'Celecoxib'],
    'Migraine': ['Sumatriptan', 'Propranolol', 'Topiramate', 'Amitriptyline']
}

LAB_TESTS = {
    'LAB_RESULT': [
        ('Hemoglobin A1c', '%', 4.0, 6.5),
        ('Total Cholesterol', 'mg/dL', 120, 200),
        ('LDL Cholesterol', 'mg/dL', 70, 130),
        ('HDL Cholesterol', 'mg/dL', 40, 60),
        ('Triglycerides', 'mg/dL', 50, 150),
        ('Creatinine', 'mg/dL', 0.6, 1.2),
        ('eGFR', 'mL/min/1.73m²', 60, 120),
        ('TSH', 'mIU/L', 0.4, 4.0),
        ('Free T4', 'ng/dL', 0.8, 1.8),
        ('Glucose', 'mg/dL', 70, 100)
    ],
    'VITAL_SIGN': [
        ('Blood Pressure Systolic', 'mmHg', 90, 140),
        ('Blood Pressure Diastolic', 'mmHg', 60, 90),
        ('Heart Rate', 'bpm', 60, 100),
        ('Temperature', '°F', 97.0, 99.5),
        ('Respiratory Rate', 'breaths/min', 12, 20),
        ('Oxygen Saturation', '%', 95, 100)
    ]
}

def generate_patient_id():
    """Generate anonymized patient ID"""
    return f"P{random.randint(100000, 999999)}"

def generate_demographics():
    """Generate realistic demographic data"""
    age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '66-75', '76+']
    genders = ['M', 'F', 'O']
    races = ['WHITE', 'BLACK', 'ASIAN', 'NATIVE', 'PACIFIC', 'OTHER']
    ethnicities = ['HISPANIC', 'NON_HISPANIC', 'UNKNOWN']
    zip_prefixes = ['100', '200', '300', '400', '500', '600', '700', '800', '900']
    
    return {
        'age_group': random.choice(age_groups),
        'gender': random.choice(genders),
        'race': random.choice(races),
        'ethnicity': random.choice(ethnicities),
        'zip_code_prefix': random.choice(zip_prefixes)
    }

def generate_diagnosis_data(specialty):
    """Generate diagnosis data based on specialty"""
    diagnoses = DIAGNOSES.get(specialty, DIAGNOSES['INTERNAL MEDICINE'])
    primary_diagnosis = random.choice(diagnoses)
    
    # Generate secondary diagnoses
    secondary_diagnoses = []
    if random.random() < 0.6:  # 60% chance of having secondary diagnoses
        secondary_count = random.randint(1, 3)
        available_diagnoses = [d for d in diagnoses if d != primary_diagnosis]
        secondary_diagnoses = random.sample(available_diagnoses, min(secondary_count, len(available_diagnoses)))
    
    # Generate comorbidities
    comorbidities = []
    if random.random() < 0.4:  # 40% chance of comorbidities
        comorbidity_count = random.randint(1, 2)
        all_diagnoses = [d for specialty_diags in DIAGNOSES.values() for d in specialty_diags]
        comorbidities = random.sample(all_diagnoses, min(comorbidity_count, len(all_diagnoses)))
    
    return {
        'primary_diagnosis': primary_diagnosis,
        'secondary_diagnoses': '; '.join(secondary_diagnoses),
        'comorbidities': '; '.join(comorbidities)
    }

def generate_treatment_data(primary_diagnosis):
    """Generate treatment data based on diagnosis"""
    treatments = TREATMENTS.get(primary_diagnosis, ['Standard Care'])
    current_treatments = random.sample(treatments, min(random.randint(1, 3), len(treatments)))
    
    # Generate treatment history
    treatment_history = []
    if random.random() < 0.7:  # 70% chance of treatment history
        history_count = random.randint(1, 3)
        all_treatments = [t for treatment_list in TREATMENTS.values() for t in treatment_list]
        treatment_history = random.sample(all_treatments, min(history_count, len(all_treatments)))
    
    return {
        'current_treatments': '; '.join(current_treatments),
        'treatment_history': '; '.join(treatment_history)
    }

def generate_lab_values():
    """Generate realistic lab values"""
    lab_values = {}
    for test_name, unit, min_val, max_val in LAB_TESTS['LAB_RESULT']:
        value = round(random.uniform(min_val, max_val), 1)
        lab_values[test_name] = f"{value} {unit}"
    return lab_values

def generate_vital_signs():
    """Generate realistic vital signs"""
    vitals = {}
    for vital_name, unit, min_val, max_val in LAB_TESTS['VITAL_SIGN']:
        value = round(random.uniform(min_val, max_val), 1)
        vitals[vital_name] = f"{value} {unit}"
    return vitals

def generate_emr_data_points(patient, num_points=20):
    """Generate EMR data points for a patient"""
    data_points = []
    
    # Generate lab results
    for test_name, unit, min_val, max_val in LAB_TESTS['LAB_RESULT']:
        value = round(random.uniform(min_val, max_val), 1)
        is_abnormal = value < min_val * 0.8 or value > max_val * 1.2
        severity = 'High' if is_abnormal and (value < min_val * 0.6 or value > max_val * 1.4) else 'Normal'
        
        data_points.append(EMRDataPoint(
            patient=patient,
            data_type='LAB_RESULT',
            metric_name=test_name,
            value=f"{value} {unit}",
            unit=unit,
            date_recorded=patient.last_visit_date - timedelta(days=random.randint(0, 30)),
            is_abnormal=is_abnormal,
            severity=severity if is_abnormal else ''
        ))
    
    # Generate vital signs
    for vital_name, unit, min_val, max_val in LAB_TESTS['VITAL_SIGN']:
        value = round(random.uniform(min_val, max_val), 1)
        is_abnormal = value < min_val * 0.9 or value > max_val * 1.1
        severity = 'High' if is_abnormal and (value < min_val * 0.8 or value > max_val * 1.3) else 'Normal'
        
        data_points.append(EMRDataPoint(
            patient=patient,
            data_type='VITAL_SIGN',
            metric_name=vital_name,
            value=f"{value} {unit}",
            unit=unit,
            date_recorded=patient.last_visit_date - timedelta(days=random.randint(0, 7)),
            is_abnormal=is_abnormal,
            severity=severity if is_abnormal else ''
        ))
    
    # Generate additional data points
    additional_data = [
        ('MEDICATION', 'Medication Adherence', random.choice(['Excellent', 'Good', 'Fair', 'Poor'])),
        ('SYMPTOM', 'Pain Level', f"{random.randint(1, 10)}/10"),
        ('SYMPTOM', 'Fatigue Level', random.choice(['Mild', 'Moderate', 'Severe'])),
        ('RISK_FACTOR', 'Smoking Status', random.choice(['Never', 'Former', 'Current'])),
        ('RISK_FACTOR', 'Family History', random.choice(['Positive', 'Negative', 'Unknown']))
    ]
    
    for data_type, metric_name, value in additional_data:
        data_points.append(EMRDataPoint(
            patient=patient,
            data_type=data_type,
            metric_name=metric_name,
            value=value,
            date_recorded=patient.last_visit_date - timedelta(days=random.randint(0, 14))
        ))
    
    return data_points

def generate_patient_outcomes(patient):
    """Generate treatment outcomes for a patient"""
    outcomes = []
    treatments = patient.current_treatments.split('; ') if patient.current_treatments else []
    
    for treatment in treatments:
        outcome_choices = ['IMPROVED', 'STABLE', 'DETERIORATED']
        weights = [0.6, 0.3, 0.1]  # 60% improved, 30% stable, 10% deteriorated
        outcome = random.choices(outcome_choices, weights=weights)[0]
        
        duration_months = random.randint(1, 24)
        outcome_date = patient.last_visit_date - timedelta(days=random.randint(30, 365))
        
        side_effects = []
        if random.random() < 0.3:  # 30% chance of side effects
            side_effects = random.sample(['Nausea', 'Headache', 'Dizziness', 'Fatigue', 'Rash'], 
                                       random.randint(1, 2))
        
        outcomes.append(PatientOutcome(
            patient=patient,
            treatment=treatment,
            outcome=outcome,
            outcome_date=outcome_date,
            notes=f"Patient showed {outcome.lower()} response to {treatment}",
            side_effects='; '.join(side_effects),
            duration_months=duration_months
        ))
    
    return outcomes

def create_patient_clusters(hcp):
    """Create AI-driven patient clusters for an HCP"""
    patients = AnonymizedPatient.objects.filter(hcp=hcp)
    if not patients.exists():
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
        
        success_rate = (improved_outcomes / total_outcomes * 100) if total_outcomes > 0 else 0
        
        cluster = PatientCluster.objects.create(
            hcp=hcp,
            name=f"{diagnosis} Cluster",
            cluster_type='DIAGNOSIS',
            description=f"Patients with {diagnosis} showing similar treatment patterns",
            patient_count=len(patient_list),
            avg_risk_score=random.uniform(0.3, 0.8),
            primary_diagnosis=diagnosis,
            common_treatments='; '.join(TREATMENTS.get(diagnosis, ['Standard Care'])),
            success_rate=success_rate,
            cluster_center={'x': random.uniform(0, 1), 'y': random.uniform(0, 1)},
            features_used=['age_group', 'gender', 'primary_diagnosis', 'lab_values']
        )
        
        # Create cluster memberships
        for patient in patient_list:
            ClusterMembership.objects.create(
                patient=patient,
                cluster=cluster,
                similarity_score=random.uniform(0.7, 0.95)
            )
        
        # Generate cluster insights
        insights = [
            {
                'insight_type': 'TREATMENT_EFFECTIVENESS',
                'title': f'High Success Rate for {diagnosis} Treatment',
                'description': f'Patients in this cluster show {success_rate:.1f}% improvement rate',
                'confidence_score': 0.85,
                'actionable_recommendations': 'Consider this treatment protocol for similar patients'
            },
            {
                'insight_type': 'PATTERN_DISCOVERY',
                'title': f'Demographic Patterns in {diagnosis}',
                'description': 'Certain age groups and demographics respond better to treatment',
                'confidence_score': 0.72,
                'actionable_recommendations': 'Tailor treatment approach based on patient demographics'
            }
        ]
        
        for insight_data in insights:
            ClusterInsight.objects.create(
                cluster=cluster,
                **insight_data,
                supporting_data={'patient_count': len(patient_list), 'success_rate': success_rate},
                is_implemented=False
            )
        
        clusters.append(cluster)
    
    return clusters

def generate_drug_recommendations(hcp, clusters):
    """Generate drug recommendations based on cluster analysis"""
    recommendations = []
    
    for cluster in clusters:
        if cluster.patient_count < 5:  # Need sufficient data
            continue
            
        # Get treatments for the primary diagnosis
        treatments = TREATMENTS.get(cluster.primary_diagnosis, ['Standard Care'])
        
        for treatment in treatments:
            # Calculate success rate for this treatment in this cluster
            success_rate = cluster.success_rate + random.uniform(-10, 10)
            success_rate = max(0, min(100, success_rate))  # Clamp between 0-100
            
            evidence_level = 'High' if success_rate > 80 else 'Moderate' if success_rate > 60 else 'Low'
            priority = 'HIGH' if success_rate > 85 else 'MEDIUM' if success_rate > 70 else 'LOW'
            
            recommendation = DrugRecommendation.objects.create(
                hcp=hcp,
                cluster=cluster,
                drug_name=treatment,
                indication=cluster.primary_diagnosis,
                success_rate=success_rate,
                patient_count=cluster.patient_count,
                evidence_level=evidence_level,
                research_support=f"Based on analysis of {cluster.patient_count} similar patients",
                contraindications=random.choice(['None known', 'Pregnancy', 'Renal impairment', 'Liver disease']),
                side_effects=random.choice(['Mild nausea', 'Headache', 'Dizziness', 'Rare: allergic reaction']),
                dosage_recommendations=f"Standard dosing for {cluster.primary_diagnosis}",
                priority=priority,
                is_reviewed=False
            )
            recommendations.append(recommendation)
    
    return recommendations

def create_hcp_user_accounts():
    """Create user accounts for HCPs"""
    hcps = HCP.objects.all()
    created_accounts = []
    
    for hcp in hcps:
        # Create username from name
        username = hcp.name.lower().replace(' ', '').replace('.', '').replace('dr', '')
        if User.objects.filter(username=username).exists():
            username = f"{username}{random.randint(1, 999)}"
        
        # Create user account
        user = User.objects.create_user(
            username=username,
            email=hcp.contact_info,
            password='password123',  # Default password
            first_name=hcp.name.split()[1] if len(hcp.name.split()) > 1 else '',
            last_name=hcp.name.split()[-1] if len(hcp.name.split()) > 1 else hcp.name
        )
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            role='HCP',
            specialty=hcp.specialty
        )
        
        created_accounts.append(user)
        print(f"Created account for {hcp.name}: {username}")
    
    return created_accounts

def seed_patient_data():
    """Main function to seed all patient data"""
    print("Starting patient data seeding...")
    
    # Create HCP user accounts
    print("Creating HCP user accounts...")
    create_hcp_user_accounts()
    
    hcps = HCP.objects.all()
    total_patients = 0
    
    for hcp in hcps:
        print(f"\nProcessing HCP: {hcp.name} ({hcp.specialty})")
        
        # Generate 20-50 patients per HCP
        num_patients = random.randint(20, 50)
        
        for i in range(num_patients):
            # Generate patient data
            demographics = generate_demographics()
            diagnosis_data = generate_diagnosis_data(hcp.specialty)
            treatment_data = generate_treatment_data(diagnosis_data['primary_diagnosis'])
            
            # Create patient
            patient = AnonymizedPatient.objects.create(
                patient_id=generate_patient_id(),
                hcp=hcp,
                age_group=demographics['age_group'],
                gender=demographics['gender'],
                race=demographics['race'],
                ethnicity=demographics['ethnicity'],
                zip_code_prefix=demographics['zip_code_prefix'],
                primary_diagnosis=diagnosis_data['primary_diagnosis'],
                secondary_diagnoses=diagnosis_data['secondary_diagnoses'],
                comorbidities=diagnosis_data['comorbidities'],
                current_treatments=treatment_data['current_treatments'],
                treatment_history=treatment_data['treatment_history'],
                medication_adherence=random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
                last_lab_values=generate_lab_values(),
                vital_signs=generate_vital_signs(),
                last_visit_date=date.today() - timedelta(days=random.randint(1, 90)),
                visit_frequency=random.choice(['Monthly', 'Quarterly', 'As needed', 'Weekly']),
                emergency_visits_6m=random.randint(0, 3),
                hospitalizations_6m=random.randint(0, 2),
                risk_factors=random.choice(['Smoking', 'Obesity', 'Family history', 'None identified']),
                family_history=random.choice(['Cardiovascular disease', 'Diabetes', 'Cancer', 'None significant']),
                insurance_type=random.choice(['Private', 'Medicare', 'Medicaid', 'Uninsured']),
                medication_access=random.choice(['Good', 'Limited', 'Excellent', 'Poor'])
            )
            
            # Generate EMR data points
            emr_data_points = generate_emr_data_points(patient)
            EMRDataPoint.objects.bulk_create(emr_data_points)
            
            # Generate patient outcomes
            outcomes = generate_patient_outcomes(patient)
            PatientOutcome.objects.bulk_create(outcomes)
            
            total_patients += 1
        
        print(f"Created {num_patients} patients for {hcp.name}")
        
        # Create patient clusters
        print(f"Creating clusters for {hcp.name}...")
        clusters = create_patient_clusters(hcp)
        print(f"Created {len(clusters)} clusters")
        
        # Generate drug recommendations
        print(f"Generating drug recommendations for {hcp.name}...")
        recommendations = generate_drug_recommendations(hcp, clusters)
        print(f"Generated {len(recommendations)} drug recommendations")
    
    print(f"\nSeeding complete!")
    print(f"Total patients created: {total_patients}")
    print(f"Total HCPs processed: {hcps.count()}")
    print(f"Total clusters created: {PatientCluster.objects.count()}")
    print(f"Total drug recommendations: {DrugRecommendation.objects.count()}")

if __name__ == '__main__':
    seed_patient_data()

