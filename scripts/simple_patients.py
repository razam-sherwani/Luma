import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import *
import random
from datetime import datetime, timedelta

# Get HCPs
hcps = HCP.objects.all()
if not hcps:
    print("No HCPs found")
    exit()

print(f"Creating 100 patients...")

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
        primary_diagnosis=random.choice(['Diabetes', 'Hypertension', 'Heart Disease', 'Cancer', 'Depression']),
        last_visit_date=datetime.now().date() - timedelta(days=random.randint(1, 90)),
        visit_frequency='Monthly',
        emergency_visits_6m=0,
        hospitalizations_6m=0
    )
    
    # Create EMR data
    EMRDataPoint.objects.create(
        patient=patient,
        data_type='VITAL_SIGN',
        metric_name='Blood Pressure',
        value='120/80',
        date_recorded=datetime.now().date()
    )

print(f"Created {AnonymizedPatient.objects.count()} patients")
print(f"Created {EMRDataPoint.objects.count()} EMR records")


