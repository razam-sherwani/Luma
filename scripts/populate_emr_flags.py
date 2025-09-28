#!/usr/bin/env python
"""
Populate EMR Flags with more interesting and diverse data
"""
import os
import django
import random
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import EMRData, HCP

def create_interesting_emr_data():
    """Create diverse and interesting EMR flags"""
    
    # Clear existing EMR data
    EMRData.objects.all().delete()
    print("Cleared existing EMR data")
    
    # Get all HCPs
    hcps = list(HCP.objects.all())
    if not hcps:
        print("No HCPs found! Run seed data first.")
        return
    
    print(f"Found {len(hcps)} HCPs")
    
    # Interesting EMR metrics by specialty
    emr_data_templates = {
        'CARDIOLOGY': [
            {'metric': 'Cardiac Arrest Cases', 'values': ['↑ 15%', '↓ 8%', '+3 this week', '12 total this month']},
            {'metric': 'Heart Transplant Referrals', 'values': ['↑ 22%', '+5 new patients', '3 urgent cases', '8 pending approvals']},
            {'metric': 'Stent Placement Success Rate', 'values': ['95.2%', '↑ 3.1%', '45/47 procedures', '98% this quarter']},
            {'metric': 'Hypertension Control Rate', 'values': ['78%', '↑ 12%', '156/200 patients', 'Target: 80%']},
            {'metric': 'Post-MI Recovery Time', 'values': ['↓ 18%', 'Avg: 6.2 days', '↓ 2.1 days', 'Best in network']},
        ],
        'ORTHOPEDIC': [
            {'metric': 'Joint Replacement Volume', 'values': ['↑ 28%', '+12 surgeries', '45 this month', '18% increase']},
            {'metric': 'ACL Reconstruction Outcomes', 'values': ['97% success', '↑ 5%', '32/33 successful', 'Top performer']},
            {'metric': 'Fracture Healing Time', 'values': ['↓ 15%', 'Avg: 8.1 weeks', '↓ 1.4 weeks', 'Excellent results']},
            {'metric': 'Spinal Fusion Complications', 'values': ['↓ 45%', '2.1% rate', 'Best in region', '↓ 3.2%']},
            {'metric': 'Post-Op Mobility Score', 'values': ['8.7/10', '↑ 0.8', '↑ 9.2%', 'Exceeds target']},
        ],
        'ONCOLOGY': [
            {'metric': 'Immunotherapy Response Rate', 'values': ['72%', '↑ 18%', '36/50 patients', 'Above average']},
            {'metric': 'Early Detection Rate', 'values': ['↑ 32%', 'Stage I: 68%', '↑ 15 cases', 'Screening success']},
            {'metric': 'Chemotherapy Adherence', 'values': ['91%', '↑ 7%', 'Best practice', '182/200 patients']},
            {'metric': 'Survivorship Program', 'values': ['+45 enrollees', '↑ 67%', '234 active', 'Program expanding']},
            {'metric': 'Palliative Care Integration', 'values': ['↑ 28%', '85% satisfaction', 'Earlier referrals', 'Quality improvement']},
        ],
        'NEUROLOGY': [
            {'metric': 'Stroke Response Time', 'values': ['↓ 23%', 'Avg: 18 mins', '↓ 5.4 mins', 'Door-to-needle']},
            {'metric': 'Epilepsy Seizure Control', 'values': ['84%', '↑ 9%', '126/150 patients', 'Medication optimization']},
            {'metric': 'MS Relapse Prevention', 'values': ['↓ 41%', '0.8 per year', '↓ 55%', 'Treatment success']},
            {'metric': 'Parkinson Mobility Score', 'values': ['7.2/10', '↑ 1.1', '↑ 18%', 'DBS candidates']},
            {'metric': 'Migraine-Free Days', 'values': ['↑ 35%', 'Avg: 22/month', '↑ 5.8 days', 'Prevention working']},
        ],
        'GASTROENTEROLOGY': [
            {'metric': 'Colonoscopy Completion Rate', 'values': ['98.5%', '↑ 2.1%', '394/400 procedures', 'Quality metric']},
            {'metric': 'IBD Remission Rate', 'values': ['76%', '↑ 14%', '95/125 patients', 'Biologic therapy']},
            {'metric': 'Liver Transplant Referrals', 'values': ['+8 patients', '↑ 33%', 'MELD scores', 'Urgent priority']},
            {'metric': 'GERD Management Success', 'values': ['89%', '↑ 6%', 'PPI optimization', '267/300 patients']},
            {'metric': 'Hepatitis C Cure Rate', 'values': ['97%', '↑ 2%', '35/36 patients', 'DAA therapy']},
        ],
        'PULMONOLOGY': [
            {'metric': 'COPD Exacerbation Rate', 'values': ['↓ 38%', '1.2 per year', '↓ 0.7', 'Prevention success']},
            {'metric': 'Sleep Apnea Compliance', 'values': ['82%', '↑ 15%', 'CPAP usage', '6.8 hrs/night']},
            {'metric': 'Lung Transplant Evaluation', 'values': ['+12 referrals', '↑ 24%', 'Wait list', 'Multidisciplinary']},
            {'metric': 'Asthma Control Score', 'values': ['8.1/10', '↑ 0.9', '↑ 12%', 'Inhaler technique']},
            {'metric': 'Pulmonary Rehab Graduation', 'values': ['91%', '↑ 8%', '73/80 patients', 'Exercise capacity']},
        ],
        'ENDOCRINOLOGY': [
            {'metric': 'Diabetes HbA1c Target', 'values': ['68%', '↑ 11%', '<7% achieved', '204/300 patients']},
            {'metric': 'Thyroid Function Stability', 'values': ['94%', '↑ 3%', 'TSH in range', 'Medication titration']},
            {'metric': 'Insulin Pump Adoption', 'values': ['↑ 45%', '+38 patients', 'CGM integration', 'Technology upgrade']},
            {'metric': 'Diabetic Retinopathy Screening', 'values': ['92%', '↑ 8%', 'Annual compliance', 'Ophthalmology referral']},
            {'metric': 'Osteoporosis T-score Improvement', 'values': ['73%', '↑ 0.6', 'Bisphosphonate therapy', 'DEXA results']},
        ],
        'NEPHROLOGY': [
            {'metric': 'Dialysis Access Patency', 'values': ['89%', '↑ 7%', 'Fistula maintenance', 'Vascular surgery']},
            {'metric': 'CKD Progression Rate', 'values': ['↓ 22%', 'eGFR stable', 'ACE inhibitor', 'BP control']},
            {'metric': 'Transplant Candidacy', 'values': ['+15 evaluations', '↑ 25%', 'Wait list active', 'Multiorgan assessment']},
            {'metric': 'Hypertension in CKD', 'values': ['71%', '↑ 9%', '<130/80 achieved', 'Medication optimization']},
            {'metric': 'Peritoneal Dialysis Success', 'values': ['85%', '↑ 12%', 'Home therapy', 'Patient education']},
        ]
    }
    
    # General metrics for any specialty
    general_metrics = [
        {'metric': 'Patient Satisfaction Score', 'values': ['4.8/5', '↑ 0.3', '94% positive', 'Top 5%']},
        {'metric': 'Readmission Rate', 'values': ['↓ 31%', '8.2%', '↓ 3.7%', 'Quality improvement']},
        {'metric': 'Average Length of Stay', 'values': ['↓ 18%', '3.2 days', '↓ 0.7 days', 'Efficiency gains']},
        {'metric': 'Telehealth Adoption', 'values': ['↑ 156%', '45% of visits', '+289 virtual', 'Patient preference']},
        {'metric': 'Clinical Trial Enrollment', 'values': ['↑ 67%', '+23 patients', '12 active studies', 'Research participation']},
        {'metric': 'Care Team Communication', 'values': ['9.1/10', '↑ 0.6', 'Nurse satisfaction', 'Workflow optimization']},
        {'metric': 'Medication Adherence', 'values': ['87%', '↑ 9%', 'Pharmacy coordination', 'Patient education']},
        {'metric': 'Preventive Care Compliance', 'values': ['83%', '↑ 14%', 'Screening rates', 'Population health']},
    ]
    
    created_count = 0
    
    # Create EMRData for each HCP
    for hcp in hcps:
        # Determine specialty-specific metrics
        specialty = hcp.specialty.upper()
        specialty_metrics = []
        
        # Map specialty to our data templates
        for key in emr_data_templates.keys():
            if key in specialty:
                specialty_metrics = emr_data_templates[key]
                break
        
        # If no specialty match, use general metrics
        if not specialty_metrics:
            specialty_metrics = general_metrics
        
        # Select 2-4 random metrics for this HCP
        num_metrics = random.randint(2, 4)
        selected_metrics = random.sample(specialty_metrics + general_metrics, min(num_metrics, len(specialty_metrics + general_metrics)))
        
        # Create EMR entries for the past week
        for i, metric_data in enumerate(selected_metrics):
            days_ago = random.randint(0, 7)
            emr_date = date.today() - timedelta(days=days_ago)
            
            emr = EMRData.objects.create(
                hcp=hcp,
                metric_name=metric_data['metric'],
                value=random.choice(metric_data['values']),
                date=emr_date
            )
            created_count += 1
    
    print(f"✅ Created {created_count} interesting EMR records!")
    
    # Show sample of what was created
    recent_emr = EMRData.objects.order_by('-date')[:10]
    print("\nSample EMR data created:")
    for emr in recent_emr:
        print(f"- {emr.hcp.name} ({emr.hcp.specialty}): {emr.metric_name} = {emr.value}")

if __name__ == "__main__":
    create_interesting_emr_data()