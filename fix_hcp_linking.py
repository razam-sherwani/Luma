#!/usr/bin/env python
"""
Fix HCP user linking issue
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import HCP, UserProfile

def fix_hcp_linking():
    print("Fixing HCP user linking...")
    
    # Get all HCP users
    hcp_users = User.objects.filter(userprofile__role='HCP')
    print(f"Found {hcp_users.count()} HCP users")
    
    for user in hcp_users:
        print(f"\nProcessing user: {user.username}")
        
        # Check if user already has an HCP record
        try:
            existing_hcp = HCP.objects.get(user=user)
            print(f"  ✓ Already linked to HCP: {existing_hcp.name}")
            continue
        except HCP.DoesNotExist:
            pass
        
        # Get user profile for specialty info
        try:
            user_profile = UserProfile.objects.get(user=user)
            specialty = user_profile.specialty or 'General Medicine'
        except UserProfile.DoesNotExist:
            specialty = 'General Medicine'
        
        # Create HCP record for this user
        hcp = HCP.objects.create(
            name=f"Dr. {user.get_full_name() or user.username}",
            specialty=specialty,
            contact_info=f"{user.email or 'No email provided'}",
            user=user
        )
        
        print(f"  ✓ Created HCP: {hcp.name} ({specialty})")
    
    print(f"\n✅ Successfully processed {hcp_users.count()} HCP users")
    
    # Verify the fix
    print("\n=== VERIFICATION ===")
    linked_hcps = HCP.objects.filter(user__isnull=False)
    print(f"HCPs with linked users: {linked_hcps.count()}")
    
    for hcp in linked_hcps[:5]:
        print(f"  {hcp.name} -> {hcp.user.username}")

if __name__ == '__main__':
    fix_hcp_linking()




