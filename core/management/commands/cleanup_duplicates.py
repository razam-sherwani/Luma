from django.core.management.base import BaseCommand
from core.models import HCP, AnonymizedPatient, User, UserProfile
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Clean up duplicate HCPs and consolidate patients'

    def handle(self, *args, **options):
        print("🧹 Starting cleanup of duplicate HCPs...")
        
        # Get all HCPs grouped by name
        hcps = HCP.objects.all()
        hcp_groups = {}
        
        for hcp in hcps:
            name = hcp.name
            if name not in hcp_groups:
                hcp_groups[name] = []
            hcp_groups[name].append(hcp)
        
        # Process each group
        cleaned_hcps = []
        total_patients_moved = 0
        
        for name, hcp_list in hcp_groups.items():
            if len(hcp_list) == 1:
                # No duplicates, keep as is
                cleaned_hcps.append(hcp_list[0])
                continue
            
            print(f"\n📋 Processing {name} ({len(hcp_list)} duplicates)")
            
            # Find the HCP with the most patients (keep this one)
            hcp_with_most_patients = max(hcp_list, key=lambda h: AnonymizedPatient.objects.filter(hcp=h).count())
            patients_count = AnonymizedPatient.objects.filter(hcp=hcp_with_most_patients).count()
            
            print(f"   ✅ Keeping HCP ID {hcp_with_most_patients.id} with {patients_count} patients")
            
            # Move patients from other HCPs to the main one
            for hcp in hcp_list:
                if hcp.id == hcp_with_most_patients.id:
                    continue
                
                # Move patients
                patients_to_move = AnonymizedPatient.objects.filter(hcp=hcp)
                moved_count = patients_to_move.count()
                
                if moved_count > 0:
                    patients_to_move.update(hcp=hcp_with_most_patients)
                    total_patients_moved += moved_count
                    print(f"   📦 Moved {moved_count} patients from HCP ID {hcp.id}")
                
                # Delete the duplicate HCP and its user
                if hcp.user:
                    print(f"   🗑️  Deleting user account: {hcp.user.username}")
                    hcp.user.delete()
                
                print(f"   🗑️  Deleting duplicate HCP ID {hcp.id}")
                hcp.delete()
            
            cleaned_hcps.append(hcp_with_most_patients)
        
        # Final summary
        print(f"\n✅ CLEANUP COMPLETE!")
        print(f"📊 Summary:")
        print(f"   • HCPs before: {len(hcps)}")
        print(f"   • HCPs after: {len(cleaned_hcps)}")
        print(f"   • Patients moved: {total_patients_moved}")
        print(f"   • Total patients: {AnonymizedPatient.objects.count()}")
        
        # Show final distribution
        print(f"\n👨‍⚕️ FINAL HCP DISTRIBUTION:")
        for hcp in cleaned_hcps:
            patient_count = AnonymizedPatient.objects.filter(hcp=hcp).count()
            username = hcp.user.username if hcp.user else "No account"
            print(f"   {hcp.name} ({hcp.specialty}): {patient_count} patients - {username}")
        
        print(f"\n🎉 Database is now clean and organized!")

