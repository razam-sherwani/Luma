from django.core.management.base import BaseCommand
from core.models import HCP

class Command(BaseCommand):
    help = 'List all HCP login credentials'

    def handle(self, *args, **options):
        hcps = HCP.objects.filter(user__isnull=False).select_related('user')
        
        self.stdout.write(self.style.SUCCESS('\n=== HCP Login Credentials ===\n'))
        
        for hcp in hcps:
            username = hcp.user.username
            specialty = hcp.specialty
            patient_count = hcp.patients.count()
            
            self.stdout.write(
                f"👨‍⚕️ {hcp.name} ({specialty})"
            )
            self.stdout.write(
                f"   Username: {username}"
            )
            self.stdout.write(
                f"   Password: password123"
            )
            self.stdout.write(
                f"   Patients: {patient_count}"
            )
            self.stdout.write("")
        
        self.stdout.write(
            self.style.SUCCESS(f'Total HCPs with accounts: {hcps.count()}')
        )


