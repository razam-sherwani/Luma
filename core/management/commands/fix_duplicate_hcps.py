from django.core.management.base import BaseCommand
from core.models import HCP, AnonymizedPatient
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Fix duplicate HCPs and get accurate patient counts'

    def handle(self, *args, **options):
        # Get all HCPs
        hcps = HCP.objects.all()
        
        # Group by name to find duplicates
        hcp_groups = {}
        for hcp in hcps:
            name = hcp.name
            if name not in hcp_groups:
                hcp_groups[name] = []
            hcp_groups[name].append(hcp)
        
        print("=== HCP DUPLICATES ===")
        duplicates_found = False
        for name, hcp_list in hcp_groups.items():
            if len(hcp_list) > 1:
                duplicates_found = True
                print(f"\n{name} has {len(hcp_list)} duplicates:")
                for i, hcp in enumerate(hcp_list):
                    patient_count = AnonymizedPatient.objects.filter(hcp=hcp).count()
                    has_user = hcp.user is not None
                    print(f"  {i+1}. ID {hcp.id}: {patient_count} patients, User: {has_user}")
        
        if not duplicates_found:
            print("No duplicates found!")
        
        print(f"\n=== SUMMARY ===")
        print(f"Total HCPs: {hcps.count()}")
        print(f"Total patients: {AnonymizedPatient.objects.count()}")
        print(f"HCPs with users: {HCP.objects.filter(user__isnull=False).count()}")
        
        # Show patient distribution
        print(f"\n=== PATIENT DISTRIBUTION ===")
        for hcp in HCP.objects.filter(user__isnull=False).order_by('name'):
            patient_count = AnonymizedPatient.objects.filter(hcp=hcp).count()
            print(f"{hcp.name}: {patient_count} patients")



