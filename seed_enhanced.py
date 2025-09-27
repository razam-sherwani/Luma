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

print("Creating comprehensive healthcare network dataset...")

# Create a more diverse set of HCPs with varying practice sizes
hcp_data = [
    # Oncology Specialists
    {'name': 'Dr. Sarah Chen', 'specialty': 'Oncology', 'contact_info': 'sarah.chen@cancercenter.org', 'region': 'Northeast'},
    {'name': 'Dr. Marcus Rodriguez', 'specialty': 'Oncology', 'contact_info': 'marcus.rodriguez@oncologygroup.com', 'region': 'West'},
    {'name': 'Dr. Emily Johnson', 'specialty': 'Hematology-Oncology', 'contact_info': 'emily.johnson@bloodcancer.org', 'region': 'Southeast'},
    
    # Cardiology Specialists
    {'name': 'Dr. Michael Thompson', 'specialty': 'Cardiology', 'contact_info': 'michael.thompson@heartinstitute.org', 'region': 'Midwest'},
    {'name': 'Dr. Priya Sharma', 'specialty': 'Interventional Cardiology', 'contact_info': 'priya.sharma@cardiaccare.com', 'region': 'West'},
    {'name': 'Dr. James Wilson', 'specialty': 'Cardiology', 'contact_info': 'james.wilson@hearthealth.net', 'region': 'Northeast'},
    
    # Endocrinology Specialists
    {'name': 'Dr. Lisa Wang', 'specialty': 'Endocrinology', 'contact_info': 'lisa.wang@diabetescenter.org', 'region': 'West'},
    {'name': 'Dr. Robert Martinez', 'specialty': 'Endocrinology', 'contact_info': 'robert.martinez@metabolichealth.com', 'region': 'Southeast'},
    {'name': 'Dr. Jennifer Brooks', 'specialty': 'Pediatric Endocrinology', 'contact_info': 'jennifer.brooks@childrensdm.org', 'region': 'Northeast'},
    
    # Neurology Specialists
    {'name': 'Dr. David Park', 'specialty': 'Neurology', 'contact_info': 'david.park@neuroinstitute.org', 'region': 'Midwest'},
    {'name': 'Dr. Amanda Foster', 'specialty': 'Movement Disorders', 'contact_info': 'amanda.foster@parkinsonscenter.com', 'region': 'West'},
    {'name': 'Dr. Christopher Lee', 'specialty': 'Neurology', 'contact_info': 'christopher.lee@braincenter.net', 'region': 'Southeast'},
    
    # Rheumatology & Other Specialties
    {'name': 'Dr. Maria Gonzalez', 'specialty': 'Rheumatology', 'contact_info': 'maria.gonzalez@arthritiscenter.org', 'region': 'Southwest'},
    {'name': 'Dr. Kevin O\'Connor', 'specialty': 'Gastroenterology', 'contact_info': 'kevin.oconnor@digestivehealth.com', 'region': 'Northeast'},
    {'name': 'Dr. Rachel Kim', 'specialty': 'Dermatology', 'contact_info': 'rachel.kim@skincancer.org', 'region': 'West'},
    
    # Primary Care with Specialization
    {'name': 'Dr. Thomas Anderson', 'specialty': 'Internal Medicine', 'contact_info': 'thomas.anderson@primarycare.org', 'region': 'Midwest'},
    {'name': 'Dr. Nicole Davis', 'specialty': 'Family Medicine', 'contact_info': 'nicole.davis@familyhealth.com', 'region': 'Southeast'},
    {'name': 'Dr. Paul Singh', 'specialty': 'Internal Medicine', 'contact_info': 'paul.singh@internalmedicine.net', 'region': 'Northeast'},
]

hcps = []
for hcp_info in hcp_data:
    hcp = HCP.objects.create(
        name=hcp_info['name'],
        specialty=hcp_info['specialty'],
        contact_info=hcp_info['contact_info']
    )
    hcps.append(hcp)

print(f"Created {len(hcps)} HCPs across diverse specialties")

# Create comprehensive research updates
research_data = [
    {'headline': 'CAR-T Cell Therapy Shows 90% Complete Response in Relapsed B-Cell Lymphoma', 'specialty': 'Hematology-Oncology', 'date': date.today() - timedelta(days=1)},
    {'headline': 'New PD-L1 Inhibitor Extends Survival in Triple-Negative Breast Cancer', 'specialty': 'Oncology', 'date': date.today() - timedelta(days=3)},
    {'headline': 'Breakthrough: PCSK9 Inhibitor Reduces Cardiac Events by 60%', 'specialty': 'Cardiology', 'date': date.today() - timedelta(days=2)},
    {'headline': 'Revolutionary TAVR Procedure Now Approved for Low-Risk Patients', 'specialty': 'Interventional Cardiology', 'date': date.today() - timedelta(days=5)},
    {'headline': 'Continuous Glucose Monitoring Reduces Diabetes Complications by 45%', 'specialty': 'Endocrinology', 'date': date.today() - timedelta(days=4)},
    {'headline': 'GLP-1 Agonists Show Neuroprotective Effects Beyond Diabetes', 'specialty': 'Endocrinology', 'date': date.today() - timedelta(days=7)},
    {'headline': 'New Monoclonal Antibody Prevents Migraine Episodes by 70%', 'specialty': 'Neurology', 'date': date.today() - timedelta(days=6)},
    {'headline': 'Deep Brain Stimulation Advances for Parkinson\'s Disease', 'specialty': 'Movement Disorders', 'date': date.today() - timedelta(days=8)},
    {'headline': 'JAK Inhibitors Transform Rheumatoid Arthritis Treatment Landscape', 'specialty': 'Rheumatology', 'date': date.today() - timedelta(days=10)},
    {'headline': 'Immunotherapy Breakthrough for Melanoma Metastases', 'specialty': 'Dermatology', 'date': date.today() - timedelta(days=12)},
    {'headline': 'Novel IBD Treatment Induces Long-Term Remission in Crohn\'s Disease', 'specialty': 'Gastroenterology', 'date': date.today() - timedelta(days=9)},
    {'headline': 'AI-Powered Risk Assessment Improves Primary Care Outcomes', 'specialty': 'Internal Medicine', 'date': date.today() - timedelta(days=14)},
]

research_updates = []
for research_info in research_data:
    research = ResearchUpdate.objects.create(**research_info)
    research_updates.append(research)

print(f"Created {len(research_updates)} research updates")

# Create diverse patient cohorts with realistic patient volumes
cohort_data = [
    # Cancer Cohorts
    {'name': 'Advanced Non-Small Cell Lung Cancer', 'description': 'Stage III-IV NSCLC patients eligible for immunotherapy', 'condition': 'Lung Cancer', 'specialty': 'Oncology', 'patient_count': 85},
    {'name': 'HER2+ Breast Cancer Patients', 'description': 'Early and metastatic HER2-positive breast cancer cases', 'condition': 'Breast Cancer', 'specialty': 'Oncology', 'patient_count': 120},
    {'name': 'Relapsed B-Cell Lymphoma', 'description': 'Patients with relapsed/refractory diffuse large B-cell lymphoma', 'condition': 'Lymphoma', 'specialty': 'Hematology-Oncology', 'patient_count': 45},
    {'name': 'Acute Myeloid Leukemia', 'description': 'Newly diagnosed and relapsed AML patients', 'condition': 'Leukemia', 'specialty': 'Hematology-Oncology', 'patient_count': 32},
    {'name': 'Metastatic Melanoma', 'description': 'Stage IV melanoma patients with BRAF mutations', 'condition': 'Melanoma', 'specialty': 'Dermatology', 'patient_count': 67},
    
    # Cardiovascular Cohorts
    {'name': 'High-Risk CAD Patients', 'description': 'Coronary artery disease with multiple vessel involvement', 'condition': 'Coronary Artery Disease', 'specialty': 'Cardiology', 'patient_count': 200},
    {'name': 'Heart Failure with Reduced EF', 'description': 'HFrEF patients on optimal medical therapy', 'condition': 'Heart Failure', 'specialty': 'Cardiology', 'patient_count': 150},
    {'name': 'Severe Aortic Stenosis', 'description': 'Patients eligible for transcatheter aortic valve replacement', 'condition': 'Aortic Stenosis', 'specialty': 'Interventional Cardiology', 'patient_count': 78},
    {'name': 'Familial Hypercholesterolemia', 'description': 'Genetic hypercholesterolemia requiring aggressive lipid management', 'condition': 'Hypercholesterolemia', 'specialty': 'Cardiology', 'patient_count': 95},
    
    # Endocrine Cohorts
    {'name': 'Complex Type 2 Diabetes', 'description': 'T2DM with cardiovascular complications and poor glycemic control', 'condition': 'Type 2 Diabetes', 'specialty': 'Endocrinology', 'patient_count': 180},
    {'name': 'Type 1 Diabetes on Pump Therapy', 'description': 'T1DM patients using continuous glucose monitoring and insulin pumps', 'condition': 'Type 1 Diabetes', 'specialty': 'Endocrinology', 'patient_count': 110},
    {'name': 'Pediatric Type 1 Diabetes', 'description': 'Children and adolescents with newly diagnosed T1DM', 'condition': 'Pediatric Diabetes', 'specialty': 'Pediatric Endocrinology', 'patient_count': 65},
    {'name': 'Thyroid Cancer Post-Surgery', 'description': 'Post-thyroidectomy patients requiring hormone replacement', 'condition': 'Thyroid Cancer', 'specialty': 'Endocrinology', 'patient_count': 40},
    
    # Neurological Cohorts
    {'name': 'Parkinson\'s Disease Advanced', 'description': 'PD patients with motor complications on advanced therapies', 'condition': 'Parkinson\'s Disease', 'specialty': 'Movement Disorders', 'patient_count': 75},
    {'name': 'Chronic Migraine Sufferers', 'description': 'Patients with >15 headache days per month', 'condition': 'Chronic Migraine', 'specialty': 'Neurology', 'patient_count': 125},
    {'name': 'Multiple Sclerosis RRMS', 'description': 'Relapsing-remitting MS patients on disease-modifying therapy', 'condition': 'Multiple Sclerosis', 'specialty': 'Neurology', 'patient_count': 90},
    {'name': 'Epilepsy Drug-Resistant', 'description': 'Patients with refractory epilepsy considering surgical options', 'condition': 'Epilepsy', 'specialty': 'Neurology', 'patient_count': 55},
    
    # Other Specialty Cohorts
    {'name': 'Rheumatoid Arthritis Severe', 'description': 'RA patients with inadequate response to conventional DMARDs', 'condition': 'Rheumatoid Arthritis', 'specialty': 'Rheumatology', 'patient_count': 105},
    {'name': 'Inflammatory Bowel Disease', 'description': 'Crohn\'s and ulcerative colitis requiring biologic therapy', 'condition': 'IBD', 'specialty': 'Gastroenterology', 'patient_count': 85},
    {'name': 'High-Risk Primary Care', 'description': 'Patients with multiple chronic conditions requiring coordinated care', 'condition': 'Multiple Comorbidities', 'specialty': 'Internal Medicine', 'patient_count': 250},
    {'name': 'Geriatric Complex Cases', 'description': 'Elderly patients with polypharmacy and multiple specialists', 'condition': 'Geriatric Syndromes', 'specialty': 'Family Medicine', 'patient_count': 180},
]

cohorts = []
for cohort_info in cohort_data:
    cohort = PatientCohort.objects.create(**cohort_info)
    cohorts.append(cohort)

print(f"Created {len(cohorts)} patient cohorts with total {sum(c.patient_count for c in cohorts)} patients")

# Create realistic treatment outcomes
treatment_data = [
    # Oncology Treatments
    {'cohort_idx': 0, 'treatment_name': 'Pembrolizumab + Chemotherapy', 'success_rate': 72.0, 'notes': 'First-line treatment showing superior OS'},
    {'cohort_idx': 0, 'treatment_name': 'Atezolizumab Monotherapy', 'success_rate': 65.0, 'notes': 'Second-line option with manageable toxicity'},
    {'cohort_idx': 1, 'treatment_name': 'Trastuzumab + Pertuzumab + Chemo', 'success_rate': 89.0, 'notes': 'Gold standard for HER2+ breast cancer'},
    {'cohort_idx': 1, 'treatment_name': 'T-DXd (Trastuzumab Deruxtecan)', 'success_rate': 83.0, 'notes': 'Revolutionary ADC therapy'},
    {'cohort_idx': 2, 'treatment_name': 'CAR-T Cell Therapy', 'success_rate': 91.0, 'notes': 'Exceptional response in relapsed lymphoma'},
    {'cohort_idx': 3, 'treatment_name': 'Venetoclax + Azacitidine', 'success_rate': 76.0, 'notes': 'Effective in elderly AML patients'},
    {'cohort_idx': 4, 'treatment_name': 'BRAF + MEK Inhibitor Combo', 'success_rate': 78.0, 'notes': 'Targeted therapy for BRAF mutant melanoma'},
    
    # Cardiology Treatments
    {'cohort_idx': 5, 'treatment_name': 'PCI with Drug-Eluting Stents', 'success_rate': 85.0, 'notes': 'Excellent outcomes in complex CAD'},
    {'cohort_idx': 6, 'treatment_name': 'SGLT2 Inhibitor + ACE-I + Beta-blocker', 'success_rate': 70.0, 'notes': 'Guideline-directed medical therapy'},
    {'cohort_idx': 7, 'treatment_name': 'TAVR (Transcatheter Aortic Valve)', 'success_rate': 92.0, 'notes': 'Minimally invasive with excellent results'},
    {'cohort_idx': 8, 'treatment_name': 'PCSK9 Inhibitor + High-Intensity Statin', 'success_rate': 88.0, 'notes': 'Achieves aggressive LDL targets'},
    
    # Endocrinology Treatments
    {'cohort_idx': 9, 'treatment_name': 'GLP-1 RA + SGLT2i + Metformin', 'success_rate': 74.0, 'notes': 'Triple therapy for complex T2DM'},
    {'cohort_idx': 10, 'treatment_name': 'Closed-Loop Insulin System', 'success_rate': 82.0, 'notes': 'Automated insulin delivery system'},
    {'cohort_idx': 11, 'treatment_name': 'CGM + Insulin Pump Therapy', 'success_rate': 85.0, 'notes': 'Pediatric diabetes technology'},
    
    # Neurology Treatments
    {'cohort_idx': 13, 'treatment_name': 'Deep Brain Stimulation', 'success_rate': 80.0, 'notes': 'Significant improvement in motor symptoms'},
    {'cohort_idx': 14, 'treatment_name': 'CGRP Monoclonal Antibody', 'success_rate': 68.0, 'notes': 'Preventive migraine therapy'},
    {'cohort_idx': 15, 'treatment_name': 'Ocrelizumab', 'success_rate': 75.0, 'notes': 'Highly effective DMT for RRMS'},
    
    # Other Specialties
    {'cohort_idx': 17, 'treatment_name': 'JAK Inhibitor (Tofacitinib)', 'success_rate': 71.0, 'notes': 'Oral targeted therapy for RA'},
    {'cohort_idx': 18, 'treatment_name': 'Anti-TNF Biologic', 'success_rate': 77.0, 'notes': 'First-line biologic for IBD'},
]

treatment_outcomes = []
for treatment_info in treatment_data:
    outcome = TreatmentOutcome.objects.create(
        cohort=cohorts[treatment_info['cohort_idx']],
        treatment_name=treatment_info['treatment_name'],
        success_rate=treatment_info['success_rate'],
        notes=treatment_info['notes']
    )
    treatment_outcomes.append(outcome)

print(f"Created {len(treatment_outcomes)} treatment outcomes")

# Create realistic HCP-Cohort connections with varying priorities
connections = []

# High-volume HCPs with multiple cohort connections
high_volume_connections = [
    # Oncology specialists with cancer cohorts
    (0, [0, 1, 4], 'HIGH'),  # Dr. Sarah Chen - Lung, Breast, Melanoma
    (1, [0, 4], 'MEDIUM'),   # Dr. Marcus Rodriguez - Lung, Melanoma
    (2, [2, 3], 'HIGH'),     # Dr. Emily Johnson - Lymphoma, Leukemia
    
    # Cardiology specialists
    (3, [5, 6, 8], 'HIGH'),  # Dr. Michael Thompson - CAD, HF, Hypercholesterolemia
    (4, [7], 'HIGH'),        # Dr. Priya Sharma - Aortic Stenosis (specialized)
    (5, [5, 6], 'MEDIUM'),   # Dr. James Wilson - CAD, HF
    
    # Endocrinology
    (6, [9, 10, 12], 'HIGH'), # Dr. Lisa Wang - T2DM, T1DM, Thyroid
    (7, [9], 'MEDIUM'),       # Dr. Robert Martinez - T2DM
    (8, [11], 'HIGH'),        # Dr. Jennifer Brooks - Pediatric Diabetes
    
    # Neurology
    (9, [14, 15, 16], 'MEDIUM'), # Dr. David Park - Migraine, MS, Epilepsy
    (10, [13], 'HIGH'),          # Dr. Amanda Foster - Parkinson's (specialized)
    (11, [14, 15], 'MEDIUM'),    # Dr. Christopher Lee - Migraine, MS
    
    # Other specialties
    (12, [17], 'HIGH'),     # Dr. Maria Gonzalez - RA
    (13, [18], 'HIGH'),     # Dr. Kevin O'Connor - IBD
    (14, [4], 'MEDIUM'),    # Dr. Rachel Kim - Melanoma
    
    # Primary Care with complex patients
    (15, [19, 8], 'MEDIUM'), # Dr. Thomas Anderson - Complex, Hypercholesterolemia
    (16, [20], 'HIGH'),      # Dr. Nicole Davis - Geriatric
    (17, [19, 9], 'MEDIUM'), # Dr. Paul Singh - Complex, T2DM
]

cohort_recommendations = []
for hcp_idx, cohort_indices, priority in high_volume_connections:
    hcp = hcps[hcp_idx]
    for cohort_idx in cohort_indices:
        cohort = cohorts[cohort_idx]
        
        # Generate realistic recommendation titles and messages
        titles = [
            f"New Treatment Protocol Available for {cohort.condition}",
            f"Patient Outcomes Opportunity in {cohort.condition}",
            f"Clinical Trial Enrollment for {cohort.name}",
            f"Updated Guidelines for {cohort.condition} Management",
            f"Breakthrough Therapy Option for {cohort.name}"
        ]
        
        messages = [
            f"Based on recent analysis, {cohort.patient_count} patients in your {cohort.name} cohort could benefit from our latest therapeutic approach.",
            f"New clinical data shows significant improvement in {cohort.condition} outcomes. Your {cohort.patient_count} patients are ideal candidates.",
            f"Exclusive access to cutting-edge {cohort.condition} treatment. Perfect match for your {cohort.name} patient population.",
            f"Updated treatment protocols for {cohort.condition} show 25% better outcomes. {cohort.patient_count} patients could benefit.",
            f"Revolutionary approach to {cohort.condition} management. Your expertise with {cohort.name} makes this a perfect fit."
        ]
        
        recommendation = CohortRecommendation.objects.create(
            hcp=hcp,
            cohort=cohort,
            title=random.choice(titles),
            message=random.choice(messages),
            priority=priority,
            is_read=random.choice([True, False, False])  # Most unread for demo
        )
        cohort_recommendations.append(recommendation)

print(f"Created {len(cohort_recommendations)} HCP-cohort recommendations")

# Create diverse EMR data showing patient volume trends
emr_metrics = [
    'Patient Volume Trend',
    'Treatment Response Rate', 
    'New Patient Referrals',
    'Complex Cases',
    'Clinical Trial Enrollment',
    'Specialty Consultation Rate'
]

emr_values = {
    'Patient Volume Trend': ['25% Increase', '15% Increase', '10% Increase', 'Stable', '5% Decrease'],
    'Treatment Response Rate': ['85-90%', '75-85%', '70-75%', '60-70%', '90%+'],
    'New Patient Referrals': ['High', 'Increasing', 'Moderate', 'Stable', 'Low'],
    'Complex Cases': ['High Complexity', 'Moderate Complexity', 'Mixed Complexity', 'Low Complexity'],
    'Clinical Trial Enrollment': ['Active Enrollment', 'Seeking Patients', 'Full Enrollment', 'Not Currently Enrolling'],
    'Specialty Consultation Rate': ['High Demand', 'Moderate Demand', 'Stable Demand', 'Low Demand']
}

for hcp in hcps:
    for _ in range(random.randint(3, 6)):  # 3-6 metrics per HCP
        metric = random.choice(emr_metrics)
        value = random.choice(emr_values[metric])
        EMRData.objects.create(
            hcp=hcp,
            metric_name=metric,
            value=value,
            date=date.today() - timedelta(days=random.randint(0, 30))
        )

# Create realistic engagement history
engagement_notes = [
    "Discussed new immunotherapy protocol - very interested in patient enrollment",
    "Reviewed clinical trial data, requesting additional safety information",
    "Positive feedback on treatment outcomes, wants to expand patient cohort", 
    "Concerned about side effects, discussed mitigation strategies",
    "Excellent response to therapy, considering additional indications",
    "Requested peer consultation and case studies",
    "Interested in combination therapy approach",
    "Discussed health economics and patient access programs",
    "Positive meeting about expanding treatment to broader population",
    "Reviewed latest research data, very engaged and asking detailed questions",
    "Scheduled follow-up to discuss patient case studies",
    "Expressed interest in being a key opinion leader for this therapy"
]

for hcp in hcps:
    # Create varied engagement history (some HCPs more engaged than others) 
    num_engagements = random.randint(2, 8)
    for _ in range(num_engagements):
        Engagement.objects.create(
            hcp=hcp,
            date=date.today() - timedelta(days=random.randint(5, 90)),
            note=random.choice(engagement_notes)
        )

# Create sample HCP users (for demo purposes)
hcp_users = []
specialties = ['Oncology', 'Cardiology', 'Endocrinology', 'Neurology', 'Rheumatology']
for i, specialty in enumerate(specialties, 1):
    username = f"hcp_user_{i}"
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            password='demo123',
            first_name=f'Dr. Demo {i}',
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
        'title': 'Revolutionary CAR-T Therapy Now Available',
        'message': 'Based on your oncology practice, breakthrough CAR-T cell therapy shows 91% complete response rates in relapsed lymphoma. Your patient profile is ideal for this therapy.',
        'priority': 'HIGH'
    },
    {
        'title': 'TAVR Procedure Expansion Opportunity', 
        'message': 'New guidelines now approve TAVR for low-risk patients. Your cardiology practice could benefit 78+ patients with this minimally invasive approach.',
        'priority': 'HIGH'
    },
    {
        'title': 'Closed-Loop Insulin System Breakthrough',
        'message': 'Revolutionary automated insulin delivery shows 82% success rate in diabetes management. Perfect for your complex Type 1 diabetes patients.',
        'priority': 'MEDIUM'
    },
    {
        'title': 'CGRP Migraine Prevention Innovation',
        'message': 'New monthly CGRP injection prevents migraines in 68% of chronic sufferers. Excellent opportunity for your neurology practice.',
        'priority': 'MEDIUM'
    },
    {
        'title': 'JAK Inhibitor Transforms RA Treatment',
        'message': 'Oral JAK inhibitor shows 71% response rate in rheumatoid arthritis. Game-changing alternative to injected biologics for your patients.',
        'priority': 'HIGH'
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

print("\n🎉 Database seeded successfully!")
print(f"📋 Created comprehensive healthcare network:")
print(f"   • {len(hcps)} HCPs across {len(set(h.specialty for h in hcps))} specialties")
print(f"   • {len(cohorts)} patient cohorts ({sum(c.patient_count for c in cohorts):,} total patients)")
print(f"   • {len(cohort_recommendations)} HCP-cohort connections")
print(f"   • {len(treatment_outcomes)} treatment outcomes")
print(f"   • {len(research_updates)} research updates")
print(f"   • {EMRData.objects.count()} EMR data points")
print(f"   • {Engagement.objects.count()} engagement records")
print("\n🔬 Sample HCP users for testing:")
print("   Usernames: hcp_user_1, hcp_user_2, hcp_user_3, hcp_user_4, hcp_user_5")
print("   Password: demo123")
print("\n🕸️ Network features:")
print("   • High-volume HCPs with 200-250 patients")
print("   • Specialized HCPs with focused patient populations") 
print("   • Complex treatment protocols with realistic success rates")  
print("   • Cross-specialty patient cohorts for interesting network patterns")
print("   • Varied engagement levels to show relationship strength")