import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import HCP, ResearchUpdate, EMRData, Engagement, UserProfile, HCRRecommendation, PatientCohort, TreatmentOutcome, CohortRecommendation, ActionableInsight
from django.contrib.auth.models import User

# Clear existing data
HCP.objects.all().delete()
ResearchUpdate.objects.all().delete()
EMRData.objects.all().delete()
Engagement.objects.all().delete()
HCRRecommendation.objects.all().delete()
PatientCohort.objects.all().delete()
TreatmentOutcome.objects.all().delete()
CohortRecommendation.objects.all().delete()
ActionableInsight.objects.all().delete()
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

# Create sample patient cohorts
cohorts_data = [
    {
        'name': 'Advanced Melanoma Patients',
        'description': 'Patients with stage III/IV melanoma requiring aggressive treatment',
        'condition': 'Advanced Melanoma',
        'specialty': 'Oncology',
        'patient_count': 25
    },
    {
        'name': 'Type 2 Diabetes with Complications',
        'description': 'Diabetic patients with neuropathy, nephropathy, or retinopathy',
        'condition': 'Type 2 Diabetes with Complications',
        'specialty': 'Endocrinology',
        'patient_count': 40
    },
    {
        'name': 'High-Risk Cardiac Patients',
        'description': 'Patients with multiple cardiac risk factors requiring intervention',
        'condition': 'High-Risk Cardiovascular Disease',
        'specialty': 'Cardiology',
        'patient_count': 30
    },
    {
        'name': 'Pediatric Asthma Patients',
        'description': 'Children with moderate to severe asthma requiring regular monitoring',
        'condition': 'Pediatric Asthma',
        'specialty': 'Pediatrics',
        'patient_count': 35
    },
    {
        'name': 'Migraine Patients',
        'description': 'Adults with chronic migraine requiring preventive treatment',
        'condition': 'Chronic Migraine',
        'specialty': 'Neurology',
        'patient_count': 20
    }
]

cohorts = []
for cohort_data in cohorts_data:
    cohort = PatientCohort.objects.create(**cohort_data)
    cohorts.append(cohort)

# Create treatment outcomes for cohorts
treatment_outcomes = [
    # Oncology treatments
    {
        'cohort': cohorts[0],  # Advanced Melanoma
        'treatment_name': 'PD-1 Inhibitor (Pembrolizumab)',
        'success_rate': 70.0,
        'side_effects': 'Mild fatigue, rash in 20% of patients',
        'notes': 'Best outcomes in patients with high PD-L1 expression'
    },
    {
        'cohort': cohorts[0],  # Advanced Melanoma
        'treatment_name': 'Combination Immunotherapy (IPI + NIVO)',
        'success_rate': 85.0,
        'side_effects': 'More severe but manageable with proper monitoring',
        'notes': 'IPI + NIVO combination shows superior results'
    },
    # Endocrinology treatments
    {
        'cohort': cohorts[1],  # Type 2 Diabetes with Complications
        'treatment_name': 'Continuous Glucose Monitoring + SGLT2 Inhibitor',
        'success_rate': 65.0,
        'side_effects': 'Minimal - occasional UTI risk',
        'notes': 'Reduces progression of complications by 40%'
    },
    {
        'cohort': cohorts[1],  # Type 2 Diabetes with Complications
        'treatment_name': 'GLP-1 Agonist + Metformin',
        'success_rate': 75.0,
        'side_effects': 'Nausea in first month, weight loss benefit',
        'notes': 'Superior glucose control with cardiovascular benefits'
    },
    # Cardiology treatments
    {
        'cohort': cohorts[2],  # High-Risk Cardiac Patients
        'treatment_name': 'Biodegradable Drug-Eluting Stent',
        'success_rate': 90.0,
        'side_effects': 'Standard stent placement risks',
        'notes': 'Reduces restenosis by 40% compared to traditional stents'
    },
    # Pediatrics treatments
    {
        'cohort': cohorts[3],  # Pediatric Asthma
        'treatment_name': 'Biologic Therapy (Omalizumab)',
        'success_rate': 80.0,
        'side_effects': 'Rare allergic reactions, injection site reactions',
        'notes': 'Reduces exacerbations by 50% in severe asthma'
    },
    # Neurology treatments
    {
        'cohort': cohorts[4],  # Chronic Migraine
        'treatment_name': 'CGRP Monoclonal Antibody (Erenumab)',
        'success_rate': 60.0,
        'side_effects': 'Constipation, injection site reactions',
        'notes': 'Monthly injection reduces migraine days by 50%'
    }
]

for outcome_data in treatment_outcomes:
    TreatmentOutcome.objects.create(**outcome_data)

# Create actionable insights
actionable_insights_data = [
    {
        'hcp': hcps[0],  # Dr. Alice Smith - Oncology
        'insight_type': 'MISSING_TREATMENT',
        'title': 'Immunotherapy Underutilization Detected',
        'description': 'Dr. Alice Smith has 15+ patients with advanced melanoma who could benefit from new immunotherapy protocols. Current treatment patterns show 60% are on older regimens.',
        'priority_score': 85,
        'patient_impact': 15,
        'research_update': research_updates[0]
    },
    {
        'hcp': hcps[1],  # Dr. Bob Jones - Cardiology
        'insight_type': 'TREATMENT_GAP',
        'title': 'Cardiac Stent Technology Gap',
        'description': 'Dr. Bob Jones performs 20+ stent procedures monthly but may not be using latest biodegradable stent technology that reduces restenosis by 40%.',
        'priority_score': 75,
        'patient_impact': 20,
        'research_update': research_updates[1]
    },
    {
        'hcp': hcps[2],  # Dr. Carol Lee - Endocrinology
        'insight_type': 'PATIENT_COHORT',
        'title': 'Diabetes Management Optimization Opportunity',
        'description': 'Dr. Carol Lee has 50+ Type 2 diabetes patients. New continuous glucose monitoring shows 40% better control rates.',
        'priority_score': 80,
        'patient_impact': 50,
        'research_update': research_updates[2]
    },
    {
        'hcp': hcps[3],  # Dr. David Kim - Neurology
        'insight_type': 'NEW_RESEARCH',
        'title': 'Migraine Prevention Breakthrough Available',
        'description': 'Dr. David Kim has 25+ chronic migraine patients. New CGRP monoclonal antibody shows 60% success rate with monthly injection.',
        'priority_score': 70,
        'patient_impact': 25,
        'research_update': research_updates[4]
    },
    {
        'hcp': hcps[4],  # Dr. Eva Patel - Pediatrics
        'insight_type': 'PATIENT_COHORT',
        'title': 'Pediatric Asthma Biologic Opportunity',
        'description': 'Dr. Eva Patel has 30+ severe asthma patients. New biologic therapy reduces exacerbations by 50% in pediatric population.',
        'priority_score': 75,
        'patient_impact': 30,
        'research_update': research_updates[3]
    }
]

for insight_data in actionable_insights_data:
    ActionableInsight.objects.create(**insight_data)

# Create cohort recommendations
cohort_recommendations_data = [
    {
        'hcp': hcps[0],  # Oncology
        'cohort': cohorts[0],  # Advanced Melanoma
        'treatment_outcome': TreatmentOutcome.objects.filter(cohort=cohorts[0]).first(),
        'title': 'Optimize Treatment for Advanced Melanoma',
        'message': f'Your {cohorts[0].patient_count} patients with {cohorts[0].condition} could benefit from combination immunotherapy. Success rate: 85%. IPI + NIVO combination shows superior results.',
        'priority': 'HIGH'
    },
    {
        'hcp': hcps[2],  # Endocrinology
        'cohort': cohorts[1],  # Type 2 Diabetes with Complications
        'treatment_outcome': TreatmentOutcome.objects.filter(cohort=cohorts[1]).first(),
        'title': 'Optimize Treatment for Type 2 Diabetes with Complications',
        'message': f'Your {cohorts[1].patient_count} patients with {cohorts[1].condition} could benefit from continuous glucose monitoring + SGLT2 inhibitor. Success rate: 65%. Reduces progression of complications by 40%.',
        'priority': 'HIGH'
    },
    {
        'hcp': hcps[1],  # Cardiology
        'cohort': cohorts[2],  # High-Risk Cardiac Patients
        'treatment_outcome': TreatmentOutcome.objects.filter(cohort=cohorts[2]).first(),
        'title': 'Optimize Treatment for High-Risk Cardiovascular Disease',
        'message': f'Your {cohorts[2].patient_count} patients with {cohorts[2].condition} could benefit from biodegradable drug-eluting stents. Success rate: 90%. Reduces restenosis by 40% compared to traditional stents.',
        'priority': 'HIGH'
    }
]

for rec_data in cohort_recommendations_data:
    CohortRecommendation.objects.create(**rec_data)

print('Database seeded successfully!')
print('Sample HCP users created with usernames: hcp_user_1, hcp_user_2, hcp_user_3, hcp_user_4, hcp_user_5')
print('Password for all demo HCP users: demo123')
print('New intelligent features added:')
print('- Patient cohort clustering and analysis')
print('- Actionable insights for HCRs')
print('- Treatment outcome tracking')
print('- Cohort-based recommendations')

