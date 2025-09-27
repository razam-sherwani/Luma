import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import HCP, ResearchUpdate, EMRData, Engagement, UserProfile, HCRRecommendation
from django.contrib.auth.models import User

# Clear existing data
HCP.objects.all().delete()
ResearchUpdate.objects.all().delete()
EMRData.objects.all().delete()
Engagement.objects.all().delete()
HCRRecommendation.objects.all().delete()
# Keep existing users but clear their profiles
UserProfile.objects.all().delete()

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

# Create sample HCP users (for demo purposes)
hcp_users = []
specialties = ['Oncology', 'Cardiology', 'Endocrinology', 'Neurology', 'Pediatrics']
for i, specialty in enumerate(specialties, 1):
    username = f"hcp_user_{i}"
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            password='demo123',
            first_name=f'Dr. Sample {i}',
            email=f'hcp{i}@hospital.com'
        )
        UserProfile.objects.create(
            user=user,
            role='HCP',
            specialty=specialty
        )
        hcp_users.append(user)

# Create sample HCR recommendations for HCP users
recommendations_data = [
    {
        'title': 'New Immunotherapy Protocol Available',
        'message': 'Based on your oncology practice, we have exciting new immunotherapy options that could benefit your patients with advanced melanoma. The latest trial data shows 70% response rates.',
        'priority': 'HIGH'
    },
    {
        'title': 'Updated Cardiac Stent Guidelines',
        'message': 'Recent cardiology guidelines have been updated for stent placement procedures. New biodegradable options show improved long-term outcomes.',
        'priority': 'MEDIUM'
    },
    {
        'title': 'Diabetes Management Innovation',
        'message': 'Revolutionary continuous glucose monitoring system now available. Patients report 40% better glucose control with this new technology.',
        'priority': 'HIGH'
    },
    {
        'title': 'Pediatric Vaccine Schedule Update',
        'message': 'New recommendations for pediatric vaccination schedules have been released. Updated timing could improve immune response by 25%.',
        'priority': 'MEDIUM'
    },
    {
        'title': 'Migraine Prevention Breakthrough',
        'message': 'New monthly injection for migraine prevention shows promise. 80% of patients experienced 50% reduction in migraine frequency.',
        'priority': 'LOW'
    }
]

for i, (user, rec_data) in enumerate(zip(hcp_users, recommendations_data)):
    HCRRecommendation.objects.create(
        hcp_user=user,
        title=rec_data['title'],
        message=rec_data['message'],
        research_update=research_updates[i] if i < len(research_updates) else None,
        priority=rec_data['priority'],
        is_read=False
    )

print('Database seeded successfully!')
print('Sample HCP users created with usernames: hcp_user_1, hcp_user_2, hcp_user_3, hcp_user_4, hcp_user_5')
print('Password for all demo HCP users: demo123')
