import os
import django
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.models import HCP, UserProfile
from django.contrib.auth.models import User

def generate_username(name):
    """Generate a username from HCP name"""
    # Remove 'Dr.' and convert to lowercase, replace spaces with dots
    clean_name = name.replace('Dr. ', '').lower()
    parts = clean_name.split()
    if len(parts) >= 2:
        username = f"{parts[0]}.{parts[1]}"
    else:
        username = parts[0]
    
    # Remove any special characters
    username = ''.join(c for c in username if c.isalnum() or c == '.')
    return username

def generate_password():
    """Generate a simple but secure password"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def create_hcp_user_accounts():
    """Create user accounts for all HCPs"""
    print("Creating user accounts for HCPs...")
    
    hcps = HCP.objects.filter(user__isnull=True)
    created_accounts = []
    
    for hcp in hcps:
        # Generate username
        base_username = generate_username(hcp.name)
        username = base_username
        
        # Ensure username is unique
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Generate password
        password = generate_password()
        
        # Create user account
        user = User.objects.create_user(
            username=username,
            password=password,
            email=f"{username}@Pulse.demo",
            first_name=hcp.name.replace('Dr. ', '').split()[0] if 'Dr. ' in hcp.name else hcp.name.split()[0],
            last_name=' '.join(hcp.name.replace('Dr. ', '').split()[1:]) if len(hcp.name.replace('Dr. ', '').split()) > 1 else ''
        )
        
        # Link user to HCP
        hcp.user = user
        hcp.save()
        
        # Create UserProfile for HCP
        UserProfile.objects.create(
            user=user,
            role='HCP',
            specialty=hcp.specialty
        )
        
        created_accounts.append({
            'name': hcp.name,
            'username': username,
            'password': password,
            'specialty': hcp.specialty
        })
        
        print(f"✅ Created account for {hcp.name}: {username}")
    
    return created_accounts

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
        
        for specialty, hcps in specialties.items():
            f.write(f"\n--- {specialty} ---\n")
            for hcp in hcps:
                f.write(f"Dr. {hcp['name']}\n")
                f.write(f"  Username: {hcp['username']}\n")
                f.write(f"  Password: {hcp['password']}\n")
                f.write(f"  Role: HCP ({hcp['specialty']})\n\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("Note: All passwords are randomly generated for security.\n")
        f.write("You can change passwords through the Django admin or in the app.\n")

def create_summary_table(accounts):
    """Create a summary table for easy reference"""
    print("\n" + "=" * 80)
    print("HCP LOGIN CREDENTIALS CREATED")
    print("=" * 80)
    print(f"{'Name':<25} {'Username':<20} {'Password':<12} {'Specialty':<20}")
    print("-" * 80)
    
    for account in accounts[:10]:  # Show first 10
        name = account['name'][:24] if len(account['name']) > 24 else account['name']
        specialty = account['specialty'][:19] if len(account['specialty']) > 19 else account['specialty']
        print(f"{name:<25} {account['username']:<20} {account['password']:<12} {specialty:<20}")
    
    if len(accounts) > 10:
        print(f"... and {len(accounts) - 10} more (see data/hcp_credentials.txt for complete list)")
    
    print("-" * 80)
    print(f"Total HCP accounts created: {len(accounts)}")
    print("Complete credentials saved to: data/hcp_credentials.txt")

def main():
    """Main function to create HCP user accounts"""
    print("Creating login accounts for all HCPs...")
    print("=" * 50)
    
    # Create user accounts
    accounts = create_hcp_user_accounts()
    
    if not accounts:
        print("All HCPs already have user accounts!")
        return
    
    # Create credentials file
    create_credentials_file(accounts)
    
    # Show summary
    create_summary_table(accounts)
    
    print("\n🎉 All HCP user accounts created successfully!")
    print("📋 Check 'data/hcp_credentials.txt' for complete login information")
    print("🔑 You can now log in as any HCP to test their dashboard view")
    print("🏥 Each HCP will see their own patients and clusters when logged in")

if __name__ == '__main__':
    main()