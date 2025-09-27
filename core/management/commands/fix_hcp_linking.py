from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import HCP, UserProfile

class Command(BaseCommand):
    help = 'Fix HCP linking issues for test users'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Fixing HCP linking issues...')
        
        # Check hcp_test user
        try:
            user = User.objects.get(username='hcp_test')
            self.stdout.write(f'✅ Found user: {user.username}')
            
            # Check if HCP exists for this user
            hcp = HCP.objects.filter(user=user).first()
            if hcp:
                self.stdout.write(f'✅ HCP already linked: {hcp.name}')
            else:
                # Find an unlinked HCP or create one
                unlinked_hcp = HCP.objects.filter(user__isnull=True).first()
                if unlinked_hcp:
                    unlinked_hcp.user = user
                    unlinked_hcp.save()
                    self.stdout.write(f'✅ Linked existing HCP: {unlinked_hcp.name}')
                else:
                    # Create a new HCP for this user
                    hcp = HCP.objects.create(
                        name=f'Dr. {user.username.title()}',
                        specialty='General Practice',
                        user=user,
                        contact_info=f'{user.email or "test@example.com"}'
                    )
                    self.stdout.write(f'✅ Created new HCP: {hcp.name}')
        except User.DoesNotExist:
            self.stdout.write('❌ hcp_test user not found')
        
        # Check all HCP users
        self.stdout.write('\n📊 Current HCP Status:')
        for hcp in HCP.objects.all():
            user_info = f" - {hcp.user.username}" if hcp.user else " - NO USER"
            self.stdout.write(f'  {hcp.name}: {user_info}')
        
        self.stdout.write('\n✅ HCP linking complete!')


