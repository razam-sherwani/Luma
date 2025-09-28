#!/usr/bin/env python
"""
Create 100 sample patients for the HCR test user
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import *
from django.contrib.auth.models import User

def create_patients():
    """Create 100 sample patients with EMR data"""
    
    # Get all HCPs
    hcps = list(HCP.objects.all())
    
    if not hcps:
        print("No HCPs found. Please run the seeding commands first.")
        return
    
    print(f"Creating 100 patients across {len(hcps)} HCPs...")
    
    # Create 100 sample patients
    for i in range(1, 101):
        patient_id = f'P{i:06d}'
        
        # Randomly assign to an HCP
        assigned_hcp = random.choice(hcps)
        
        # Create patient
        patient = AnonymizedPatient.objects.create(
            patient_id=patient_id,
            hcp=assigned_hcp,
            age_group=random.choice(['18-25', '26-35', '36-50', '51-65', '65+']),
            gender=random.choice(['M', 'F', 'O']),
            race=random.choice(['WHITE', 'BLACK', 'ASIAN', 'NATIVE', 'PACIFIC', 'OTHER']),
            ethnicity=random.choice(['HISPANIC', 'NON_HISPANIC', 'UNKNOWN']),
            zip_code_prefix=f'{random.randint(10000, 99999)}',
            primary_diagnosis=random.choice([
                'Type 2 Diabetes Mellitus', 'Essential Hypertension', 'Coronary Artery Disease',
                'Atrial Fibrillation', 'Heart Failure', 'Chronic Kidney Disease',
                'Hypothyroidism', 'Osteoarthritis', 'Gastroesophageal Reflux Disease',
                'Irritable Bowel Syndrome', 'Migraine', 'Epilepsy', 'Parkinson Disease',
                'Multiple Sclerosis', 'Breast Cancer', 'Lung Cancer', 'Colorectal Cancer'
            ]),
            secondary_diagnoses=random.choice([
                'Hyperlipidemia', 'Obesity', 'Depression', 'Anxiety', 'Sleep Apnea',
                'Asthma', 'COPD', 'Arthritis', 'Osteoporosis', ''
            ]),
            comorbidities=random.choice([
                'Diabetes, Hypertension', 'Heart Disease, High Cholesterol',
                'Obesity, Sleep Apnea', 'Depression, Anxiety', 'Arthritis, Osteoporosis', ''
            ]),
            current_treatments=random.choice([
                'Metformin, Lisinopril', 'Atorvastatin, Aspirin', 'Insulin, Glipizide',
                'Albuterol, Prednisone', 'Sertraline, Therapy', 'Ibuprofen, Physical Therapy'
            ]),
            treatment_history=random.choice([
                'Previous metformin trial', 'Surgery 2019', 'Physical therapy 2020',
                'Medication adjustment 2021', 'No previous treatments', 'Multiple medication trials'
            ]),
            medication_adherence=random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
            last_lab_values={'glucose': random.randint(80, 200), 'cholesterol': random.randint(150, 300)},
            vital_signs={'bp_systolic': random.randint(110, 180), 'bp_diastolic': random.randint(70, 110)},
            last_visit_date=datetime.now().date() - timedelta(days=random.randint(1, 90)),
            visit_frequency=random.choice(['Monthly', 'Quarterly', 'Bi-annually', 'Annually']),
            emergency_visits_6m=random.randint(0, 3),
            hospitalizations_6m=random.randint(0, 2),
            risk_factors=random.choice([
                'Family history of diabetes', 'Smoking history', 'Sedentary lifestyle',
                'High stress', 'Poor diet', 'Multiple risk factors'
            ]),
            family_history=random.choice([
                'Mother: Diabetes', 'Father: Heart Disease', 'Sibling: Cancer',
                'Grandparent: Stroke', 'No significant family history'
            ]),
            insurance_type=random.choice(['Medicare', 'Medicaid', 'Private', 'Uninsured']),
            medication_access=random.choice(['Full access', 'Limited access', 'No access'])
        )
        
        # Create some EMR data points for each patient
        for j in range(random.randint(3, 8)):
            EMRDataPoint.objects.create(
                patient=patient,
                data_type=random.choice(['LAB_RESULT', 'VITAL_SIGN', 'DIAGNOSIS', 'MEDICATION', 'PROCEDURE']),
                metric_name=random.choice([
                    'Blood Glucose', 'Blood Pressure', 'Heart Rate', 'Cholesterol',
                    'Weight', 'Temperature', 'Hemoglobin A1C', 'Creatinine'
                ]),
                value=str(random.uniform(50, 200)),
                unit=random.choice(['mg/dL', 'mmHg', 'bpm', 'lbs', '°F', '%']),
                date_recorded=datetime.now().date() - timedelta(days=random.randint(1, 180)),
                is_abnormal=random.choice([True, False]),
                severity=random.choice(['Mild', 'Moderate', 'Severe', ''])
            )
        
        # Create treatment outcomes for some patients
        if random.random() < 0.7:  # 70% chance
            PatientOutcome.objects.create(
                patient=patient,
                treatment=random.choice(['Metformin', 'Lisinopril', 'Atorvastatin', 'Insulin', 'Physical Therapy']),
                outcome=random.choice(['IMPROVED', 'STABLE', 'DETERIORATED']),
                outcome_date=datetime.now().date() - timedelta(days=random.randint(1, 90)),
                notes=f'Treatment response for {patient.primary_diagnosis}',
                side_effects=random.choice(['None', 'Mild nausea', 'Dizziness', 'Fatigue', 'Rash']),
                duration_months=random.randint(1, 12)
            )
        
        if i % 20 == 0:
            print(f"Created {i} patients...")
    
    print(f'\n✅ Successfully created 100 patients!')
    print(f'📊 Database Summary:')
    print(f'   • Total patients: {AnonymizedPatient.objects.count()}')
    print(f'   • Total EMR data points: {EMRDataPoint.objects.count()}')
    print(f'   • Total outcomes: {PatientOutcome.objects.count()}')
    print(f'   • Patients per HCP: {AnonymizedPatient.objects.count() // len(hcps)}')

if __name__ == '__main__':
    create_patients()


