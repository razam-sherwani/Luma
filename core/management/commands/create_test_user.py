from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile

class Command(BaseCommand):
    help = 'Create a test user for login'

    def handle(self, *args, **options):
        # Create test HCR user
        hcr_user, created = User.objects.get_or_create(
            username='hcr_test',
            defaults={
                'email': 'hcr@test.com',
                'first_name': 'Test',
                'last_name': 'HCR'
            }
        )
        if created:
            hcr_user.set_password('password123')
            hcr_user.save()
            
            UserProfile.objects.create(
                user=hcr_user,
                role='HCR'
            )
            self.stdout.write(
                self.style.SUCCESS('Created HCR test user: hcr_test / password123')
            )
        else:
            self.stdout.write('HCR test user already exists')
        
        # Create test HCP user
        hcp_user, created = User.objects.get_or_create(
            username='hcp_test',
            defaults={
                'email': 'hcp@test.com',
                'first_name': 'Test',
                'last_name': 'HCP'
            }
        )
        if created:
            hcp_user.set_password('password123')
            hcp_user.save()
            
            UserProfile.objects.create(
                user=hcp_user,
                role='HCP',
                specialty='Cardiology'
            )
            self.stdout.write(
                self.style.SUCCESS('Created HCP test user: hcp_test / password123')
            )
        else:
            self.stdout.write('HCP test user already exists')
        
        self.stdout.write(
            self.style.SUCCESS('\nTest users created successfully!')
        )
        self.stdout.write('HCR Login: hcr_test / password123')
        self.stdout.write('HCP Login: hcp_test / password123')

