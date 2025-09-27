import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import HCP, ResearchUpdate, EMRData, Engagement

# Clear existing data
HCP.objects.all().delete()
ResearchUpdate.objects.all().delete()
EMRData.objects.all().delete()
Engagement.objects.all().delete()

# Create fake HCPs
hcps = [
    HCP.objects.create(name='Dr. Alice Smith', specialty='Oncology', contact_info='alice.smith@hospital.org'),
    HCP.objects.create(name='Dr. Bob Jones', specialty='Cardiology', contact_info='bob.jones@clinic.com'),
    HCP.objects.create(name='Dr. Carol Lee', specialty='Endocrinology', contact_info='carol.lee@healthcare.net'),
    HCP.objects.create(name='Dr. David Kim', specialty='Neurology', contact_info='david.kim@hospital.org'),
    HCP.objects.create(name='Dr. Eva Patel', specialty='Pediatrics', contact_info='eva.patel@clinic.com'),
]

# Create fake Research Updates
research_updates = [
    ResearchUpdate.objects.create(headline='New Immunotherapy Shows Promise in Oncology', specialty='Oncology', date=date.today()),
    ResearchUpdate.objects.create(headline='Breakthrough in Cardiac Stent Technology', specialty='Cardiology', date=date.today() - timedelta(days=2)),
    ResearchUpdate.objects.create(headline='Latest Guidelines for Diabetes Management', specialty='Endocrinology', date=date.today() - timedelta(days=5)),
    ResearchUpdate.objects.create(headline='Advances in Pediatric Vaccines', specialty='Pediatrics', date=date.today() - timedelta(days=1)),
    ResearchUpdate.objects.create(headline='Novel Treatment for Migraine Relief', specialty='Neurology', date=date.today() - timedelta(days=3)),
]

# Create fake EMR Data
emr_metrics = [
    ('Top Diagnosis', ['Hypertension', 'Diabetes', 'Asthma', 'Cancer', 'Migraine']),
    ('Patient Volume', ['Increased', 'Stable', 'Decreased']),
]
for hcp in hcps:
    for metric, values in emr_metrics:
        EMRData.objects.create(
            hcp=hcp,
            metric_name=metric,
            value=random.choice(values),
            date=date.today() - timedelta(days=random.randint(0, 10))
        )

# Create fake Engagements
notes = [
    'Called today to discuss new trial data.',
    'Emailed about recent research update.',
    'Met in person to review patient volume trends.',
    'Sent follow-up on EMR changes.',
]
for hcp in hcps:
    for i in range(2):
        Engagement.objects.create(
            hcp=hcp,
            date=date.today() - timedelta(days=random.randint(10, 40)),
            note=random.choice(notes)
        )

print('Database seeded successfully!')
