import os
import django
import random
from datetime import date, timedelta, datetime
from faker import Faker
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import (
    HCP, ResearchUpdate, EMRData, Engagement, UserProfile, HCRRecommendation, 
    PatientCohort, TreatmentOutcome, CohortRecommendation, ActionableInsight,
    AnonymizedPatient, EMRDataPoint, PatientOutcome, PatientCluster, 
    ClusterMembership, ClusterInsight, DrugRecommendation
)
from django.contrib.auth.models import User

fake = Faker()

def clear_clustering_data():
    """Clear existing clustering and patient data"""
    print("Clearing existing clustering and patient data...")
    DrugRecommendation.objects.all().delete()
    ClusterInsight.objects.all().delete()
    ClusterMembership.objects.all().delete()
    PatientCluster.objects.all().delete()
    PatientOutcome.objects.all().delete()
    EMRDataPoint.objects.all().delete()
    AnonymizedPatient.objects.all().delete()
    print("Cleared clustering and patient data")

def generate_realistic_patients():
    """Generate realistic anonymized patient data"""
    print("Generating realistic patient data...")
    
    # Get all HCPs for assignment
    hcps = list(HCP.objects.all())
    if not hcps:
        print("No HCPs found. Please run the basic seed script first.")
        return []
    
    # Common conditions by specialty
    specialty_conditions = {
        'INTERNAL MEDICINE': [
            'Type 2 Diabetes Mellitus', 'Essential Hypertension', 'Hyperlipidemia',
            'Chronic Kidney Disease', 'Gastroesophageal Reflux Disease'
        ],
        'CARDIOVASCULAR DISEASE (CARDIOLOGY)': [
            'Coronary Artery Disease', 'Heart Failure', 'Atrial Fibrillation',
            'Hypertension', 'Myocardial Infarction'
        ],
        'RADIATION ONCOLOGY': [
            'Breast Cancer', 'Lung Cancer', 'Prostate Cancer',
            'Colorectal Cancer', 'Brain Tumor'
        ],
        'ENDOCRINOLOGY': [
            'Type 1 Diabetes', 'Type 2 Diabetes', 'Thyroid Disorders',
            'Metabolic Syndrome', 'Osteoporosis'
        ],
        'NEUROLOGY': [
            'Alzheimer\'s Disease', 'Parkinson\'s Disease', 'Epilepsy',
            'Multiple Sclerosis', 'Migraine'
        ],
        'ORTHOPEDIC SURGERY': [
            'Osteoarthritis', 'Rheumatoid Arthritis', 'Fractures',
            'Spinal Disorders', 'Joint Replacement'
        ]
    }
    
    patients = []
    patient_counter = 1000  # Start with 1000 for realistic IDs
    
    # Generate 200-400 patients per HCP
    for hcp in hcps:
        patient_count = random.randint(200, 400)
        hcp_conditions = specialty_conditions.get(hcp.specialty, 
            ['Hypertension', 'Diabetes', 'Heart Disease', 'Chronic Pain'])
        
        for _ in range(patient_count):
            patient_counter += 1
            
            # Generate patient demographics
            age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '66-75', '76+']
            age_group = random.choice(age_groups)
            
            # Weight age groups towards older populations for chronic conditions
            if hcp.specialty in ['CARDIOVASCULAR DISEASE (CARDIOLOGY)', 'ENDOCRINOLOGY']:
                age_group = random.choices(age_groups, weights=[5, 10, 15, 20, 25, 20, 5])[0]
            
            gender = random.choice(['M', 'F'])
            race = random.choices(
                ['WHITE', 'BLACK', 'ASIAN', 'NATIVE', 'PACIFIC', 'OTHER'],
                weights=[60, 20, 10, 3, 2, 5]
            )[0]
            
            ethnicity = random.choices(
                ['NON_HISPANIC', 'HISPANIC', 'UNKNOWN'],
                weights=[75, 20, 5]
            )[0]
            
            primary_diagnosis = random.choice(hcp_conditions)
            
            # Generate comorbidities based on primary diagnosis
            comorbidities = []
            if 'Diabetes' in primary_diagnosis:
                comorbidities.extend(random.sample([
                    'Hypertension', 'Hyperlipidemia', 'Chronic Kidney Disease',
                    'Diabetic Retinopathy', 'Peripheral Neuropathy'
                ], random.randint(1, 3)))
            elif 'Heart' in primary_diagnosis or 'Cardiac' in primary_diagnosis:
                comorbidities.extend(random.sample([
                    'Diabetes', 'Hypertension', 'Hyperlipidemia',
                    'Chronic Kidney Disease', 'Sleep Apnea'
                ], random.randint(1, 3)))
            
            # Generate current treatments based on diagnosis
            treatments = []
            if 'Diabetes' in primary_diagnosis:
                treatments.extend(random.sample([
                    'Metformin', 'Insulin', 'GLP-1 agonist', 'SGLT-2 inhibitor'
                ], random.randint(1, 3)))
            elif 'Hypertension' in primary_diagnosis:
                treatments.extend(random.sample([
                    'ACE inhibitor', 'Beta blocker', 'Calcium channel blocker', 'Diuretic'
                ], random.randint(1, 2)))
            elif 'Cancer' in primary_diagnosis:
                treatments.extend(random.sample([
                    'Chemotherapy', 'Radiation therapy', 'Immunotherapy', 'Surgery'
                ], random.randint(1, 3)))
            
            # Generate lab values based on condition
            lab_values = {}
            if 'Diabetes' in primary_diagnosis:
                lab_values = {
                    'HbA1c': round(random.uniform(6.5, 11.0), 1),
                    'Glucose': random.randint(120, 300),
                    'Creatinine': round(random.uniform(0.8, 2.5), 1),
                }
            elif 'Heart' in primary_diagnosis:
                lab_values = {
                    'BNP': random.randint(100, 1500),
                    'Troponin': round(random.uniform(0.01, 5.0), 2),
                    'Cholesterol': random.randint(180, 350),
                }
            
            # Generate vital signs
            vital_signs = {
                'BP_Systolic': random.randint(90, 180),
                'BP_Diastolic': random.randint(60, 110),
                'Heart_Rate': random.randint(50, 120),
                'Weight_lbs': random.randint(120, 300),
                'BMI': round(random.uniform(18.5, 45.0), 1),
            }
            
            patient = AnonymizedPatient.objects.create(
                patient_id=f"PT{patient_counter:06d}",
                hcp=hcp,
                age_group=age_group,
                gender=gender,
                race=race,
                ethnicity=ethnicity,
                zip_code_prefix=fake.zipcode()[:5],
                primary_diagnosis=primary_diagnosis,
                secondary_diagnoses='; '.join(random.sample([
                    'Depression', 'Anxiety', 'Chronic Pain', 'Insomnia'
                ], min(random.randint(0, 2), 4))),
                comorbidities='; '.join(comorbidities),
                current_treatments='; '.join(treatments),
                treatment_history=f"Previous treatments: {'; '.join(random.sample(treatments + ['Physical therapy', 'Lifestyle modification'], min(random.randint(1, 3), len(treatments + ['Physical therapy', 'Lifestyle modification']))))}",
                medication_adherence=random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
                last_lab_values=lab_values,
                vital_signs=vital_signs,
                last_visit_date=fake.date_between(start_date='-90d', end_date='today'),
                visit_frequency=random.choice(['Weekly', 'Bi-weekly', 'Monthly', 'Quarterly', 'As needed']),
                emergency_visits_6m=random.randint(0, 5),
                hospitalizations_6m=random.randint(0, 3),
                risk_factors='; '.join(random.sample([
                    'Smoking', 'Alcohol use', 'Sedentary lifestyle', 'Family history',
                    'Obesity', 'High stress', 'Poor diet'
                ], min(random.randint(1, 4), 7))),
                family_history='; '.join(random.sample([
                    'Diabetes', 'Heart disease', 'Cancer', 'Hypertension',
                    'Stroke', 'Mental illness'
                ], min(random.randint(0, 3), 6))),
                insurance_type=random.choice(['Medicare', 'Medicaid', 'Private', 'Uninsured']),
                medication_access=random.choice(['Full access', 'Limited access', 'Generic only', 'Difficulty affording'])
            )
            patients.append(patient)
    
    print(f"Generated {len(patients)} patient records")
    return patients

def generate_emr_data_points(patients):
    """Generate EMR data points for patients"""
    print("Generating EMR data points...")
    
    data_points = []
    
    for patient in patients[:500]:  # Limit to first 500 patients for performance
        # Generate 10-20 data points per patient
        num_points = random.randint(10, 20)
        
        for _ in range(num_points):
            data_type = random.choice(['LAB_RESULT', 'VITAL_SIGN', 'MEDICATION', 'SYMPTOM'])
            
            if data_type == 'LAB_RESULT':
                if 'Diabetes' in patient.primary_diagnosis:
                    metric_name = random.choice(['HbA1c', 'Glucose', 'Creatinine', 'Cholesterol'])
                    if metric_name == 'HbA1c':
                        value = str(round(random.uniform(6.0, 12.0), 1))
                        unit = '%'
                        is_abnormal = float(value) > 7.0
                    elif metric_name == 'Glucose':
                        value = str(random.randint(80, 350))
                        unit = 'mg/dL'
                        is_abnormal = int(value) > 140
                    else:
                        value = str(round(random.uniform(0.5, 3.0), 1))
                        unit = 'mg/dL'
                        is_abnormal = float(value) > 1.2
                else:
                    metric_name = random.choice(['Complete Blood Count', 'Basic Metabolic Panel', 'Lipid Panel'])
                    value = f"Within normal limits" if random.random() > 0.3 else "Abnormal"
                    unit = ""
                    is_abnormal = "Abnormal" in value
            
            elif data_type == 'VITAL_SIGN':
                metric_name = random.choice(['Blood Pressure', 'Heart Rate', 'Weight', 'Temperature'])
                if metric_name == 'Blood Pressure':
                    systolic = random.randint(90, 180)
                    diastolic = random.randint(60, 110)
                    value = f"{systolic}/{diastolic}"
                    unit = "mmHg"
                    is_abnormal = systolic > 140 or diastolic > 90
                elif metric_name == 'Heart Rate':
                    hr = random.randint(50, 120)
                    value = str(hr)
                    unit = "bpm"
                    is_abnormal = hr < 60 or hr > 100
                else:
                    value = str(random.randint(50, 250))
                    unit = "lbs" if metric_name == 'Weight' else "°F"
                    is_abnormal = False
            
            else:  # MEDICATION or SYMPTOM
                if data_type == 'MEDICATION':
                    metric_name = random.choice(['Metformin', 'Lisinopril', 'Atorvastatin', 'Insulin'])
                    value = "Active prescription"
                    unit = ""
                    is_abnormal = False
                else:
                    metric_name = random.choice(['Pain level', 'Fatigue', 'Shortness of breath', 'Nausea'])
                    value = str(random.randint(1, 10))
                    unit = "/10"
                    is_abnormal = int(value) > 6
            
            data_point = EMRDataPoint.objects.create(
                patient=patient,
                data_type=data_type,
                metric_name=metric_name,
                value=value,
                unit=unit,
                date_recorded=fake.date_between(start_date='-180d', end_date='today'),
                is_abnormal=is_abnormal,
                severity='High' if is_abnormal and random.random() > 0.7 else 'Low' if not is_abnormal else 'Medium'
            )
            data_points.append(data_point)
    
    print(f"Generated {len(data_points)} EMR data points")
    return data_points

def generate_patient_outcomes(patients):
    """Generate treatment outcomes for patients"""
    print("Generating patient outcomes...")
    
    outcomes = []
    
    for patient in patients[:300]:  # Limit for performance
        # Generate 1-5 outcomes per patient
        num_outcomes = random.randint(1, 5)
        
        treatments = patient.current_treatments.split('; ') if patient.current_treatments else ['Standard care']
        
        for _ in range(num_outcomes):
            treatment = random.choice(treatments)
            
            # Base outcome probabilities on patient characteristics
            if patient.medication_adherence == 'Excellent':
                outcome = random.choices(['IMPROVED', 'STABLE', 'DETERIORATED'], weights=[60, 35, 5])[0]
            elif patient.medication_adherence == 'Good':
                outcome = random.choices(['IMPROVED', 'STABLE', 'DETERIORATED'], weights=[45, 40, 15])[0]
            elif patient.medication_adherence == 'Fair':
                outcome = random.choices(['IMPROVED', 'STABLE', 'DETERIORATED'], weights=[30, 45, 25])[0]
            else:  # Poor
                outcome = random.choices(['IMPROVED', 'STABLE', 'DETERIORATED'], weights=[20, 40, 40])[0]
            
            notes = ""
            side_effects = ""
            
            if outcome == 'IMPROVED':
                notes = random.choice([
                    "Patient shows significant improvement in symptoms",
                    "Lab values trending in positive direction",
                    "Patient reports feeling much better",
                    "Clinical markers showing improvement"
                ])
            elif outcome == 'DETERIORATED':
                notes = random.choice([
                    "Patient condition has worsened despite treatment",
                    "New symptoms have emerged",
                    "Lab values showing concerning trends",
                    "Patient reports increased symptoms"
                ])
                side_effects = random.choice([
                    "Mild nausea", "Fatigue", "Dizziness", "Headache",
                    "Gastrointestinal upset", "Sleep disturbance"
                ])
            
            patient_outcome = PatientOutcome.objects.create(
                patient=patient,
                treatment=treatment,
                outcome=outcome,
                outcome_date=fake.date_between(start_date='-120d', end_date='today'),
                notes=notes,
                side_effects=side_effects,
                duration_months=random.randint(1, 12)
            )
            outcomes.append(patient_outcome)
    
    print(f"Generated {len(outcomes)} patient outcomes")
    return outcomes

def generate_patient_clusters(hcps, patients):
    """Generate AI-driven patient clusters"""
    print("Generating patient clusters...")
    
    clusters = []
    
    for hcp in hcps:
        hcp_patients = [p for p in patients if p.hcp == hcp]
        if len(hcp_patients) < 10:
            continue
        
        # Create 3-6 clusters per HCP
        num_clusters = random.randint(3, 6)
        
        for i in range(num_clusters):
            cluster_type = random.choice(['DIAGNOSIS', 'TREATMENT_RESPONSE', 'RISK_PROFILE', 'CLINICAL'])
            
            if cluster_type == 'DIAGNOSIS':
                # Group by primary diagnosis
                diagnoses = list(set([p.primary_diagnosis for p in hcp_patients]))
                primary_dx = random.choice(diagnoses)
                cluster_patients = [p for p in hcp_patients if p.primary_diagnosis == primary_dx]
                name = f"{primary_dx} Patients"
                description = f"Patients with {primary_dx} under care of {hcp.name}"
                
            elif cluster_type == 'TREATMENT_RESPONSE':
                # Group by treatment response patterns
                name = f"High Response Group {i+1}"
                description = f"Patients showing excellent response to treatment protocols"
                cluster_patients = random.sample(hcp_patients, min(random.randint(15, 40), len(hcp_patients)))
                primary_dx = random.choice([p.primary_diagnosis for p in cluster_patients])
                
            elif cluster_type == 'RISK_PROFILE':
                # Group by risk factors
                name = f"High Risk Cohort {i+1}"
                description = f"Patients with elevated risk factors requiring intensive monitoring"
                cluster_patients = random.sample(hcp_patients, min(random.randint(20, 50), len(hcp_patients)))
                primary_dx = "Multiple conditions"
                
            else:  # CLINICAL
                name = f"Clinical Pattern Group {i+1}"
                description = f"Patients with similar clinical presentations and lab patterns"
                cluster_patients = random.sample(hcp_patients, min(random.randint(25, 60), len(hcp_patients)))
                primary_dx = random.choice([p.primary_diagnosis for p in cluster_patients])
            
            if not cluster_patients:
                continue
            
            # Calculate cluster metrics
            patient_count = len(cluster_patients)
            avg_risk_score = round(random.uniform(0.2, 0.9), 2)
            success_rate = round(random.uniform(0.65, 0.95), 2)
            
            # Common treatments in cluster
            all_treatments = []
            for p in cluster_patients:
                if p.current_treatments:
                    all_treatments.extend(p.current_treatments.split('; '))
            common_treatments = '; '.join(list(set(all_treatments))[:5])
            
            # Cluster features (for AI algorithm)
            features_used = random.sample([
                'age_group', 'primary_diagnosis', 'comorbidities', 'lab_values',
                'medication_adherence', 'risk_factors', 'treatment_response'
            ], random.randint(3, 6))
            
            cluster_center = {
                'avg_age': random.choice(['35-45', '45-55', '55-65', '65+']),
                'common_diagnosis': primary_dx,
                'avg_risk': avg_risk_score,
                'response_rate': success_rate
            }
            
            cluster = PatientCluster.objects.create(
                hcp=hcp,
                name=name,
                cluster_type=cluster_type,
                description=description,
                patient_count=patient_count,
                avg_risk_score=avg_risk_score,
                primary_diagnosis=primary_dx,
                common_treatments=common_treatments,
                success_rate=success_rate,
                cluster_center=cluster_center,
                features_used=features_used
            )
            clusters.append(cluster)
            
            # Create cluster memberships
            for patient in cluster_patients:
                similarity_score = round(random.uniform(0.7, 0.98), 2)
                ClusterMembership.objects.create(
                    patient=patient,
                    cluster=cluster,
                    similarity_score=similarity_score
                )
    
    print(f"Generated {len(clusters)} patient clusters")
    return clusters

def generate_cluster_insights(clusters):
    """Generate AI insights from clusters"""
    print("Generating cluster insights...")
    
    insights = []
    
    for cluster in clusters:
        # Generate 2-4 insights per cluster
        num_insights = random.randint(2, 4)
        
        for _ in range(num_insights):
            insight_type = random.choice([
                'TREATMENT_EFFECTIVENESS', 'PATTERN_DISCOVERY', 
                'RISK_FACTORS', 'OPTIMIZATION_OPPORTUNITY'
            ])
            
            if insight_type == 'TREATMENT_EFFECTIVENESS':
                title = f"Treatment Response Analysis for {cluster.name}"
                description = f"Analysis shows {cluster.success_rate*100:.0f}% success rate in this cluster. {random.choice(['Above average performance', 'Room for improvement', 'Excellent outcomes'])} compared to similar patient populations."
                recommendations = f"Consider {random.choice(['dose optimization', 'combination therapy', 'lifestyle interventions', 'monitoring frequency adjustment'])} to improve outcomes."
                
            elif insight_type == 'PATTERN_DISCOVERY':
                title = f"Clinical Pattern Identified in {cluster.name}"
                description = f"AI analysis identified {random.choice(['medication adherence patterns', 'lab value correlations', 'symptom clusters', 'treatment response patterns'])} that predict outcomes."
                recommendations = f"Implement {random.choice(['adherence monitoring', 'predictive screening', 'early intervention protocols', 'personalized care plans'])} based on identified patterns."
                
            elif insight_type == 'RISK_FACTORS':
                title = f"Risk Factor Analysis for {cluster.name}"
                description = f"Cluster analysis reveals {random.choice(['elevated cardiovascular risk', 'increased hospitalization risk', 'medication interaction risks', 'progression risk factors'])} in {random.randint(20, 80)}% of patients."
                recommendations = f"Recommend {random.choice(['intensive monitoring', 'preventive interventions', 'risk stratification', 'medication review'])} for high-risk patients."
                
            else:  # OPTIMIZATION_OPPORTUNITY
                title = f"Care Optimization Opportunity for {cluster.name}"
                description = f"Data suggests potential for {random.randint(15, 40)}% improvement in outcomes through {random.choice(['protocol standardization', 'care coordination', 'patient education', 'technology integration'])}."
                recommendations = f"Implement {random.choice(['standardized protocols', 'care pathways', 'patient engagement tools', 'clinical decision support'])} to optimize care delivery."
            
            supporting_data = {
                'patient_count': cluster.patient_count,
                'confidence_level': round(random.uniform(0.75, 0.95), 2),
                'data_points_analyzed': random.randint(500, 2000),
                'statistical_significance': 'p < 0.05' if random.random() > 0.2 else 'p < 0.01'
            }
            
            insight = ClusterInsight.objects.create(
                cluster=cluster,
                insight_type=insight_type,
                title=title,
                description=description,
                confidence_score=round(random.uniform(0.75, 0.95), 2),
                actionable_recommendations=recommendations,
                supporting_data=supporting_data
            )
            insights.append(insight)
    
    print(f"Generated {len(insights)} cluster insights")
    return insights

def generate_drug_recommendations(hcps, clusters):
    """Generate evidence-based drug recommendations"""
    print("Generating drug recommendations...")
    
    recommendations = []
    
    # Drug database with realistic information
    drug_database = {
        'Diabetes': [
            {'name': 'Semaglutide', 'success_rate': 0.85, 'evidence': 'High', 'indication': 'Type 2 Diabetes with cardiovascular benefits'},
            {'name': 'Empagliflozin', 'success_rate': 0.78, 'evidence': 'High', 'indication': 'Type 2 Diabetes with heart failure'},
            {'name': 'Dulaglutide', 'success_rate': 0.82, 'evidence': 'Moderate', 'indication': 'Type 2 Diabetes weight management'},
        ],
        'Hypertension': [
            {'name': 'Sacubitril/Valsartan', 'success_rate': 0.79, 'evidence': 'High', 'indication': 'Heart failure with reduced ejection fraction'},
            {'name': 'Chlorthalidone', 'success_rate': 0.75, 'evidence': 'High', 'indication': 'Hypertension with cardiovascular protection'},
            {'name': 'Amlodipine/Olmesartan', 'success_rate': 0.73, 'evidence': 'Moderate', 'indication': 'Combination therapy for difficult-to-control BP'},
        ],
        'Cancer': [
            {'name': 'Pembrolizumab', 'success_rate': 0.68, 'evidence': 'High', 'indication': 'Advanced melanoma and lung cancer'},
            {'name': 'Trastuzumab deruxtecan', 'success_rate': 0.72, 'evidence': 'High', 'indication': 'HER2-positive breast cancer'},
            {'name': 'Osimertinib', 'success_rate': 0.75, 'evidence': 'High', 'indication': 'EGFR-mutated lung cancer'},
        ],
        'Heart': [
            {'name': 'Dapagliflozin', 'success_rate': 0.74, 'evidence': 'High', 'indication': 'Heart failure regardless of diabetes status'},
            {'name': 'Vericiguat', 'success_rate': 0.69, 'evidence': 'Moderate', 'indication': 'Heart failure with reduced ejection fraction'},
            {'name': 'Mavacamten', 'success_rate': 0.78, 'evidence': 'Moderate', 'indication': 'Hypertrophic cardiomyopathy'},
        ]
    }
    
    for hcp in hcps:
        hcp_clusters = [c for c in clusters if c.hcp == hcp]
        
        for cluster in hcp_clusters:
            # Find relevant drugs for this cluster
            relevant_drugs = []
            for condition, drugs in drug_database.items():
                if condition.lower() in cluster.primary_diagnosis.lower():
                    relevant_drugs.extend(drugs)
            
            if not relevant_drugs:
                # Default drugs for general conditions
                relevant_drugs = random.sample([
                    {'name': 'Metformin XR', 'success_rate': 0.72, 'evidence': 'High', 'indication': 'First-line diabetes therapy'},
                    {'name': 'Lisinopril', 'success_rate': 0.70, 'evidence': 'High', 'indication': 'ACE inhibitor for hypertension'},
                    {'name': 'Atorvastatin', 'success_rate': 0.76, 'evidence': 'High', 'indication': 'Cholesterol management'},
                ], random.randint(1, 2))
            
            # Generate 1-3 recommendations per cluster
            selected_drugs = random.sample(relevant_drugs, min(random.randint(1, 3), len(relevant_drugs)))
            
            for drug_info in selected_drugs:
                # Adjust success rate based on cluster characteristics
                base_success_rate = drug_info['success_rate']
                if cluster.avg_risk_score > 0.7:  # High risk patients
                    adjusted_success_rate = base_success_rate * 0.9  # Slightly lower success
                else:
                    adjusted_success_rate = base_success_rate * 1.05  # Slightly higher success
                
                adjusted_success_rate = min(adjusted_success_rate, 0.95)  # Cap at 95%
                
                # Generate research support
                research_support = f"Based on analysis of {cluster.patient_count} similar patients. Recent studies show {adjusted_success_rate*100:.0f}% efficacy in this population."
                
                # Generate contraindications and side effects
                contraindications = random.choice([
                    "Severe renal impairment, pregnancy",
                    "Known hypersensitivity, liver disease",
                    "Severe heart failure, pregnancy",
                    "Active bleeding, severe kidney disease"
                ])
                
                side_effects = random.choice([
                    "Mild: nausea, headache, dizziness",
                    "Common: fatigue, GI upset, dizziness",
                    "Possible: muscle pain, sleep disturbance",
                    "Monitor: liver function, kidney function"
                ])
                
                # Dosage recommendations
                dosage = random.choice([
                    "Start 5mg daily, titrate to effect",
                    "Initial dose 10mg twice daily",
                    "Begin with lowest effective dose",
                    "Standard protocol: 20mg daily"
                ])
                
                priority = 'HIGH' if adjusted_success_rate > 0.8 else 'MEDIUM' if adjusted_success_rate > 0.7 else 'LOW'
                
                recommendation = DrugRecommendation.objects.create(
                    hcp=hcp,
                    cluster=cluster,
                    drug_name=drug_info['name'],
                    indication=drug_info['indication'],
                    success_rate=round(adjusted_success_rate * 100, 1),  # Convert to percentage
                    patient_count=cluster.patient_count,
                    evidence_level=drug_info['evidence'],
                    research_support=research_support,
                    contraindications=contraindications,
                    side_effects=side_effects,
                    dosage_recommendations=dosage,
                    priority=priority
                )
                recommendations.append(recommendation)
    
    print(f"Generated {len(recommendations)} drug recommendations")
    return recommendations

def main():
    """Main function to populate database with clustering features"""
    print("Starting clustering feature database population...")
    print("=" * 60)
    
    # Clear existing clustering data
    clear_clustering_data()
    
    # Generate new data
    patients = generate_realistic_patients()
    if not patients:
        return
    
    data_points = generate_emr_data_points(patients)
    outcomes = generate_patient_outcomes(patients)
    
    # Get HCPs for clustering
    hcps = list(HCP.objects.all())
    clusters = generate_patient_clusters(hcps, patients)
    
    insights = generate_cluster_insights(clusters)
    drug_recommendations = generate_drug_recommendations(hcps, clusters)
    
    print("\n" + "=" * 60)
    print("CLUSTERING DATABASE POPULATION COMPLETE!")
    print("=" * 60)
    print(f"✅ Anonymized Patients: {len(patients)}")
    print(f"✅ EMR Data Points: {len(data_points)}")
    print(f"✅ Patient Outcomes: {len(outcomes)}")
    print(f"✅ Patient Clusters: {len(clusters)}")
    print(f"✅ Cluster Insights: {len(insights)}")
    print(f"✅ Drug Recommendations: {len(drug_recommendations)}")
    print(f"✅ Cluster Memberships: {sum(cluster.patient_count for cluster in clusters)}")
    
    print("\nNew Features Available:")
    print("🔬 Patient Database - Browse anonymized patient records")
    print("📊 AI-Driven Clustering - Patients grouped by similarity")
    print("💡 Cluster Insights - AI-generated treatment insights")
    print("💊 Drug Recommendations - Evidence-based therapy suggestions")
    print("🎯 Cohort-Cluster Network - Advanced visualization")
    
    print(f"\nYour Pulse platform now includes advanced AI clustering!")
    print("Visit http://127.0.0.1:8000/dashboard/patients/ to explore the new features.")

if __name__ == '__main__':
    main()