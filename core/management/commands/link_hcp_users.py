from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import HCP, UserProfile

class Command(BaseCommand):
    help = 'Link existing HCPs to users'

    def handle(self, *args, **options):
        # Get all HCP users
        hcp_users = User.objects.filter(userprofile__role='HCP')
        
        # Get all HCPs without users
        hcps_without_users = HCP.objects.filter(user__isnull=True)
        
        self.stdout.write(f'Found {hcp_users.count()} HCP users')
        self.stdout.write(f'Found {hcps_without_users.count()} HCPs without users')
        
        # Link HCPs to users by matching names or creating new HCPs
        for user in hcp_users:
            user_profile = UserProfile.objects.get(user=user)
            
            # Try to find existing HCP by name match
            hcp = HCP.objects.filter(name__icontains=user.username).first()
            
            if not hcp:
                # Create new HCP for this user
                hcp = HCP.objects.create(
                    name=f"Dr. {user.get_full_name() or user.username}",
                    specialty=user_profile.specialty or 'General Medicine',
                    contact_info=f"{user.email or 'No email provided'}",
                    user=user
                )
                self.stdout.write(f'Created new HCP: {hcp.name}')
            else:
                # Link existing HCP to user
                hcp.user = user
                hcp.save()
                self.stdout.write(f'Linked existing HCP: {hcp.name} to user: {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully linked HCPs to users!')
        )




