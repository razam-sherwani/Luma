from django.core.management.base import BaseCommand
from core.models import HCP, AnonymizedPatient, User, UserProfile
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Reduce patient data to 100 patients total, distributed across HCPs'

    def handle(self, *args, **options):
        print("🔢 Reducing patient data to 100 patients total...")
        
        # Get all HCPs
        hcps = HCP.objects.filter(user__isnull=False).order_by('name')
        
        if not hcps.exists():
            print("❌ No HCPs found with user accounts!")
            return
        
        # Calculate patients per HCP (roughly equal distribution)
        total_hcps = hcps.count()
        patients_per_hcp = 100 // total_hcps
        remainder = 100 % total_hcps
        
        print(f"📊 Distributing 100 patients across {total_hcps} HCPs")
        print(f"   • Base: {patients_per_hcp} patients per HCP")
        print(f"   • Extra: {remainder} patients to distribute")
        
        # Clear all existing patients
        print("🗑️  Clearing existing patients...")
        deleted_count = AnonymizedPatient.objects.count()
        AnonymizedPatient.objects.all().delete()
        print(f"   Deleted {deleted_count} patients")
        
        # Create new patients for each HCP
        import random
        from datetime import datetime, timedelta
        
        patient_id_counter = 1
        total_created = 0
        
        for i, hcp in enumerate(hcps):
            # Calculate how many patients this HCP gets
            if i < remainder:
                num_patients = patients_per_hcp + 1
            else:
                num_patients = patients_per_hcp
            
            print(f"\n👨‍⚕️ {hcp.name} ({hcp.specialty}): {num_patients} patients")
            
            # Generate patients for this HCP
            for j in range(num_patients):
                # Generate patient ID
                patient_id = f"P{patient_id_counter:06d}"
                patient_id_counter += 1
                
                # Generate demographics
                age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '66-75', '76+']
                genders = ['M', 'F', 'O']
                races = ['WHITE', 'BLACK', 'ASIAN', 'NATIVE', 'PACIFIC', 'OTHER']
                ethnicities = ['HISPANIC', 'NON_HISPANIC', 'UNKNOWN']
                zip_codes = ['10001', '20001', '30001', '40001', '50001', '60001', '70001', '80001', '90001']
                
                # Generate diagnosis based on specialty
                diagnoses = {
                    'Cardiology': ['Hypertension', 'Coronary Artery Disease', 'Heart Failure', 'Atrial Fibrillation'],
                    'Oncology': ['Breast Cancer', 'Lung Cancer', 'Prostate Cancer', 'Colon Cancer'],
                    'Neurology': ['Migraine', 'Epilepsy', 'Parkinson Disease', 'Multiple Sclerosis'],
                    'Orthopedics': ['Osteoarthritis', 'Fracture', 'Back Pain', 'Joint Replacement'],
                    'Pediatrics': ['Asthma', 'ADHD', 'Diabetes Type 1', 'Developmental Delay'],
                    'Testing': ['Test Condition A', 'Test Condition B', 'Test Condition C']
                }
                
                primary_diagnosis = random.choice(diagnoses.get(hcp.specialty, ['General Condition']))
                
                # Create patient
                patient = AnonymizedPatient.objects.create(
                    patient_id=patient_id,
                    hcp=hcp,
                    age_group=random.choice(age_groups),
                    gender=random.choice(genders),
                    race=random.choice(races),
                    ethnicity=random.choice(ethnicities),
                    zip_code_prefix=random.choice(zip_codes),
                    primary_diagnosis=primary_diagnosis,
                    secondary_diagnoses=f"Secondary condition {j+1}",
                    comorbidities=f"Comorbidity {j+1}",
                    current_treatments=f"Treatment {j+1}",
                    treatment_history=f"Previous treatment {j+1}",
                    medication_adherence=random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
                    last_lab_values={},
                    vital_signs={},
                    last_visit_date=datetime.now().date() - timedelta(days=random.randint(1, 90)),
                    visit_frequency=random.choice(['Weekly', 'Monthly', 'Quarterly', 'As needed']),
                    emergency_visits_6m=random.randint(0, 3),
                    hospitalizations_6m=random.randint(0, 2),
                    risk_factors=f"Risk factor {j+1}",
                    family_history=f"Family history {j+1}",
                    insurance_type=random.choice(['Private', 'Medicare', 'Medicaid', 'Uninsured']),
                    medication_access=random.choice(['Excellent', 'Good', 'Limited', 'Poor'])
                )
                
                total_created += 1
        
        # Final summary
        print(f"\n✅ REDUCTION COMPLETE!")
        print(f"📊 Final Summary:")
        print(f"   • Total patients: {AnonymizedPatient.objects.count()}")
        print(f"   • HCPs: {hcps.count()}")
        
        # Show distribution
        print(f"\n👨‍⚕️ PATIENT DISTRIBUTION:")
        for hcp in hcps:
            patient_count = AnonymizedPatient.objects.filter(hcp=hcp).count()
            print(f"   {hcp.name}: {patient_count} patients")
        
        print(f"\n🎉 Database now has exactly 100 patients!")




