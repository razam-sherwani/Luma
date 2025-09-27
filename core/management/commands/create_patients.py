from django.core.management.base import BaseCommand
from core.models import *
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Create 100 sample patients'

    def handle(self, *args, **options):
        # Get HCPs
        hcps = list(HCP.objects.all())
        if not hcps:
            self.stdout.write(self.style.ERROR('No HCPs found. Run other seeding commands first.'))
            return

        self.stdout.write('Creating 100 patients...')
        
        # Create 100 patients
        for i in range(1, 101):
            patient = AnonymizedPatient.objects.create(
                patient_id=f'P{i:06d}',
                hcp=random.choice(hcps),
                age_group=random.choice(['18-25', '26-35', '36-50', '51-65', '65+']),
                gender=random.choice(['M', 'F']),
                race='WHITE',
                ethnicity='NON_HISPANIC',
                zip_code_prefix='12345',
                primary_diagnosis=random.choice([
                    'Type 2 Diabetes', 'Essential Hypertension', 'Coronary Artery Disease',
                    'Atrial Fibrillation', 'Heart Failure', 'Chronic Kidney Disease',
                    'Hypothyroidism', 'Osteoarthritis', 'Gastroesophageal Reflux Disease',
                    'Irritable Bowel Syndrome', 'Migraine', 'Epilepsy', 'Parkinson Disease',
                    'Multiple Sclerosis', 'Breast Cancer', 'Lung Cancer', 'Colorectal Cancer'
                ]),
                secondary_diagnoses=random.choice(['Hyperlipidemia', 'Obesity', 'Depression', 'Anxiety', '']),
                comorbidities=random.choice(['Diabetes, Hypertension', 'Heart Disease', 'Obesity', '']),
                current_treatments=random.choice([
                    'Metformin, Lisinopril', 'Atorvastatin, Aspirin', 'Insulin, Glipizide',
                    'Albuterol, Prednisone', 'Sertraline, Therapy', 'Ibuprofen, Physical Therapy'
                ]),
                treatment_history=random.choice(['Previous metformin trial', 'Surgery 2019', 'No previous treatments']),
                medication_adherence=random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
                last_lab_values={'glucose': random.randint(80, 200)},
                vital_signs={'bp_systolic': random.randint(110, 180)},
                last_visit_date=datetime.now().date() - timedelta(days=random.randint(1, 90)),
                visit_frequency=random.choice(['Monthly', 'Quarterly', 'Bi-annually', 'Annually']),
                emergency_visits_6m=random.randint(0, 2),
                hospitalizations_6m=random.randint(0, 1),
                risk_factors=random.choice(['Family history', 'Smoking', 'Sedentary lifestyle', '']),
                family_history=random.choice(['Mother: Diabetes', 'Father: Heart Disease', 'No significant history']),
                insurance_type=random.choice(['Medicare', 'Medicaid', 'Private', 'Uninsured']),
                medication_access=random.choice(['Full access', 'Limited access', 'No access'])
            )
            
            # Create EMR data points
            for j in range(random.randint(2, 5)):
                EMRDataPoint.objects.create(
                    patient=patient,
                    data_type=random.choice(['LAB_RESULT', 'VITAL_SIGN', 'DIAGNOSIS', 'MEDICATION']),
                    metric_name=random.choice([
                        'Blood Glucose', 'Blood Pressure', 'Heart Rate', 'Cholesterol',
                        'Weight', 'Temperature', 'Hemoglobin A1C', 'Creatinine'
                    ]),
                    value=str(random.uniform(50, 200)),
                    unit=random.choice(['mg/dL', 'mmHg', 'bpm', 'lbs', '°F', '%']),
                    date_recorded=datetime.now().date() - timedelta(days=random.randint(1, 180)),
                    is_abnormal=random.choice([True, False])
                )
            
            # Create treatment outcomes
            if random.random() < 0.6:  # 60% chance
                PatientOutcome.objects.create(
                    patient=patient,
                    treatment=random.choice(['Metformin', 'Lisinopril', 'Atorvastatin', 'Insulin', 'Physical Therapy']),
                    outcome=random.choice(['IMPROVED', 'STABLE', 'DETERIORATED']),
                    outcome_date=datetime.now().date() - timedelta(days=random.randint(1, 90)),
                    notes=f'Treatment response for {patient.primary_diagnosis}',
                    side_effects=random.choice(['None', 'Mild nausea', 'Dizziness', 'Fatigue']),
                    duration_months=random.randint(1, 12)
                )
            
            if i % 20 == 0:
                self.stdout.write(f'Created {i} patients...')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created 100 patients!')
        )
        self.stdout.write(f'Total patients: {AnonymizedPatient.objects.count()}')
        self.stdout.write(f'Total EMR data points: {EMRDataPoint.objects.count()}')
        self.stdout.write(f'Total outcomes: {PatientOutcome.objects.count()}')


