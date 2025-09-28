import os
import django
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import HCP, UserProfile
from django.contrib.auth.models import User

def generate_password():
    """Generate a simple but secure password"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def reset_hcp_passwords_and_create_file():
    """Reset all HCP passwords and create credentials file"""
    print("Resetting passwords for all HCPs and creating credentials file...")
    
    # Get all HCPs with user accounts
    hcps = HCP.objects.filter(user__isnull=False).order_by('specialty', 'name')
    credentials = []
    
    for hcp in hcps:
        # Generate new password
        new_password = generate_password()
        
        # Update user password
        hcp.user.set_password(new_password)
        hcp.user.save()
        
        credentials.append({
            'name': hcp.name,
            'username': hcp.user.username,
            'password': new_password,
            'specialty': hcp.specialty
        })
        
        print(f"✅ Reset password for {hcp.name}: {hcp.user.username}")
    
    # Create credentials file
    create_credentials_file(credentials)
    
    print(f"\n🎉 Reset passwords for {len(credentials)} HCPs!")
    print("📋 Check 'data/hcp_credentials.txt' for complete login information")
    
    return credentials

def create_credentials_file(accounts):
    """Create a file with all login credentials"""
    print("Creating credentials file...")
    
    with open('../data/hcp_credentials.txt', 'w') as f:
        f.write("Pulse HCP Login Credentials\n")
        f.write("=" * 50 + "\n\n")
        f.write("Use these credentials to log in as different HCPs:\n")
        f.write("URL: http://127.0.0.1:8000/accounts/login/\n\n")
        
        # Group by specialty for easier navigation
        specialties = {}
        for account in accounts:
            specialty = account['specialty']
            if specialty not in specialties:
                specialties[specialty] = []
            specialties[specialty].append(account)
        
        for specialty, hcps in sorted(specialties.items()):
            f.write(f"\n--- {specialty} ---\n")
            for hcp in hcps:
                f.write(f"{hcp['name']}\n")
                f.write(f"  Username: {hcp['username']}\n")
                f.write(f"  Password: {hcp['password']}\n")
                f.write(f"  Role: HCP ({hcp['specialty']})\n\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("Note: All passwords are randomly generated for security.\n")
        f.write("You can change passwords through the Django admin or in the app.\n")

def main():
    """Main function"""
    print("Regenerating all HCP login credentials...")
    print("=" * 50)
    
    credentials = reset_hcp_passwords_and_create_file()
    
    # Show Dr. Annette Cox specifically
    print("\n" + "=" * 50)
    print("DR. ANNETTE COX CREDENTIALS:")
    print("=" * 50)
    
    for cred in credentials:
        if 'annette' in cred['name'].lower() and 'cox' in cred['name'].lower():
            print(f"Name: {cred['name']}")
            print(f"Username: {cred['username']}")
            print(f"Password: {cred['password']}")
            print(f"Specialty: {cred['specialty']}")
            print(f"Login URL: http://127.0.0.1:8000/accounts/login/")
            break
    else:
        print("Dr. Annette Cox not found!")

if __name__ == '__main__':
    main()