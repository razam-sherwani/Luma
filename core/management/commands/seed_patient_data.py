from django.core.management.base import BaseCommand
import os
import sys
import django
import random
import json
from datetime import datetime, timedelta, date
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import (HCP, AnonymizedPatient, EMRDataPoint, PatientOutcome, 
                        PatientCluster, ClusterMembership, ClusterInsight, 
                        DrugRecommendation, UserProfile)
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Seed patient EMR data and create HCP accounts'

    def handle(self, *args, **options):
        self.stdout.write('Starting patient data seeding...')
        try:
            self.seed_patient_data()
            self.stdout.write(
                self.style.SUCCESS('Successfully seeded patient data!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error seeding data: {str(e)}')
            )

    def seed_patient_data(self):
        """Main function to seed all patient data"""
        print("Starting patient data seeding...")
        
        # Create HCP user accounts
        print("Creating HCP user accounts...")
        self.create_hcp_user_accounts()
        
        hcps = HCP.objects.all()
        total_patients = 0
        
        for hcp in hcps:
            print(f"\nProcessing HCP: {hcp.name} ({hcp.specialty})")
            
            # Generate 20-50 patients per HCP
            num_patients = random.randint(20, 50)
            
            for i in range(num_patients):
                # Generate patient data
                demographics = self.generate_demographics()
                diagnosis_data = self.generate_diagnosis_data(hcp.specialty)
                treatment_data = self.generate_treatment_data(diagnosis_data['primary_diagnosis'])
                
                # Create patient
                patient = AnonymizedPatient.objects.create(
                    patient_id=self.generate_patient_id(),
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
                    last_lab_values=self.generate_lab_values(),
                    vital_signs=self.generate_vital_signs(),
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
                emr_data_points = self.generate_emr_data_points(patient)
                EMRDataPoint.objects.bulk_create(emr_data_points)
                
                # Generate patient outcomes
                outcomes = self.generate_patient_outcomes(patient)
                PatientOutcome.objects.bulk_create(outcomes)
                
                total_patients += 1
            
            print(f"Created {num_patients} patients for {hcp.name}")
        
        print(f"\nSeeding complete!")
        print(f"Total patients created: {total_patients}")
        print(f"Total HCPs processed: {hcps.count()}")

    def generate_patient_id(self):
        """Generate anonymized patient ID"""
        return f"P{random.randint(100000, 999999)}"

    def generate_demographics(self):
        """Generate realistic demographic data"""
        age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '66-75', '76+']
        genders = ['M', 'F', 'O']
        races = ['WHITE', 'BLACK', 'ASIAN', 'NATIVE', 'PACIFIC', 'OTHER']
        ethnicities = ['HISPANIC', 'NON_HISPANIC', 'UNKNOWN']
        zip_prefixes = ['10001', '20001', '30001', '40001', '50001', '60001', '70001', '80001', '90001']
        
        return {
            'age_group': random.choice(age_groups),
            'gender': random.choice(genders),
            'race': random.choice(races),
            'ethnicity': random.choice(ethnicities),
            'zip_code_prefix': random.choice(zip_prefixes)
        }

    def generate_diagnosis_data(self, specialty):
        """Generate diagnosis data based on specialty"""
        diagnoses = {
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
        
        specialty_diagnoses = diagnoses.get(specialty, diagnoses['INTERNAL MEDICINE'])
        primary_diagnosis = random.choice(specialty_diagnoses)
        
        # Generate secondary diagnoses
        secondary_diagnoses = []
        if random.random() < 0.6:  # 60% chance of having secondary diagnoses
            secondary_count = random.randint(1, 3)
            available_diagnoses = [d for d in specialty_diagnoses if d != primary_diagnosis]
            secondary_diagnoses = random.sample(available_diagnoses, min(secondary_count, len(available_diagnoses)))
        
        # Generate comorbidities
        comorbidities = []
        if random.random() < 0.4:  # 40% chance of comorbidities
            comorbidity_count = random.randint(1, 2)
            all_diagnoses = [d for specialty_diags in diagnoses.values() for d in specialty_diags]
            comorbidities = random.sample(all_diagnoses, min(comorbidity_count, len(all_diagnoses)))
        
        return {
            'primary_diagnosis': primary_diagnosis,
            'secondary_diagnoses': '; '.join(secondary_diagnoses),
            'comorbidities': '; '.join(comorbidities)
        }

    def generate_treatment_data(self, primary_diagnosis):
        """Generate treatment data based on diagnosis"""
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
        
        patient_treatments = treatments.get(primary_diagnosis, ['Standard Care'])
        current_treatments = random.sample(patient_treatments, min(random.randint(1, 3), len(patient_treatments)))
        
        # Generate treatment history
        treatment_history = []
        if random.random() < 0.7:  # 70% chance of treatment history
            history_count = random.randint(1, 3)
            all_treatments = [t for treatment_list in treatments.values() for t in treatment_list]
            treatment_history = random.sample(all_treatments, min(history_count, len(all_treatments)))
        
        return {
            'current_treatments': '; '.join(current_treatments),
            'treatment_history': '; '.join(treatment_history)
        }

    def generate_lab_values(self):
        """Generate realistic lab values"""
        lab_values = {}
        lab_tests = [
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
        ]
        
        for test_name, unit, min_val, max_val in lab_tests:
            value = round(random.uniform(min_val, max_val), 1)
            lab_values[test_name] = f"{value} {unit}"
        return lab_values

    def generate_vital_signs(self):
        """Generate realistic vital signs"""
        vitals = {}
        vital_tests = [
            ('Blood Pressure Systolic', 'mmHg', 90, 140),
            ('Blood Pressure Diastolic', 'mmHg', 60, 90),
            ('Heart Rate', 'bpm', 60, 100),
            ('Temperature', '°F', 97.0, 99.5),
            ('Respiratory Rate', 'breaths/min', 12, 20),
            ('Oxygen Saturation', '%', 95, 100)
        ]
        
        for vital_name, unit, min_val, max_val in vital_tests:
            value = round(random.uniform(min_val, max_val), 1)
            vitals[vital_name] = f"{value} {unit}"
        return vitals

    def generate_emr_data_points(self, patient):
        """Generate EMR data points for a patient"""
        data_points = []
        
        # Generate lab results
        lab_tests = [
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
        ]
        
        for test_name, unit, min_val, max_val in lab_tests:
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
        vital_tests = [
            ('Blood Pressure Systolic', 'mmHg', 90, 140),
            ('Blood Pressure Diastolic', 'mmHg', 60, 90),
            ('Heart Rate', 'bpm', 60, 100),
            ('Temperature', '°F', 97.0, 99.5),
            ('Respiratory Rate', 'breaths/min', 12, 20),
            ('Oxygen Saturation', '%', 95, 100)
        ]
        
        for vital_name, unit, min_val, max_val in vital_tests:
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

    def generate_patient_outcomes(self, patient):
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

    def create_hcp_user_accounts(self):
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
            
            # Link user to HCP
            hcp.user = user
            hcp.save()
            
            created_accounts.append(user)
            print(f"Created account for {hcp.name}: {username} / password123")
        
        return created_accounts
