#!/usr/bin/env python
"""
Fix HCP login accounts by resetting passwords
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import HCP

def fix_hcp_logins():
    print("Fixing HCP login accounts...")
    
    # Get all HCPs with users
    hcps = HCP.objects.filter(user__isnull=False)
    print(f"Found {len(hcps)} HCPs with user accounts")
    
    # Reset passwords for all HCP users
    for hcp in hcps:
        if hcp.user:
            hcp.user.set_password('password123')
            hcp.user.save()
            print(f"Reset password for {hcp.user.username} ({hcp.name})")
    
    print(f"\n✅ Reset passwords for {len(hcps)} HCP accounts")
    print("All HCP accounts now use password: password123")
    
    # Show some sample accounts
    print("\nSample HCP accounts:")
    for hcp in hcps[:5]:
        print(f"  {hcp.user.username} / password123 - {hcp.name} ({hcp.specialty})")

if __name__ == '__main__':
    fix_hcp_logins()

