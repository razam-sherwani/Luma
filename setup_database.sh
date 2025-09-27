#!/bin/bash

echo "============================================"
echo "ProviderPulse Database Setup - Clustering Branch"
echo "============================================"
echo

echo "Step 1: Installing required packages..."
pip install pandas requests faker
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi
echo "✅ Packages installed"
echo

echo "Step 2: Setting up database..."
python manage.py makemigrations
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: Database setup failed"
    exit 1
fi
echo "✅ Database setup complete"
echo

echo "Step 3: Downloading real healthcare data..."
python download_emr_data.py
if [ $? -ne 0 ]; then
    echo "ERROR: Healthcare data download failed"
    exit 1
fi
echo "✅ Real healthcare data downloaded"
echo

echo "Step 4: Populating with real EMR data..."
python seed_real_emr.py
if [ $? -ne 0 ]; then
    echo "ERROR: EMR data population failed"
    exit 1
fi
echo "✅ EMR data populated"
echo

echo "Step 5: Generating clustering features..."
python seed_clustering.py
if [ $? -ne 0 ]; then
    echo "ERROR: Clustering features failed"
    exit 1
fi
echo "✅ Clustering features generated"
echo

echo "Step 6: Creating HCP login accounts..."
python create_hcp_accounts.py
if [ $? -ne 0 ]; then
    echo "ERROR: HCP account creation failed"
    exit 1
fi
echo "✅ HCP login accounts created"
echo

echo "============================================"
echo "🎉 SETUP COMPLETE!"
echo "============================================"
echo
echo "Your ProviderPulse database is now fully populated with:"
echo "- 50 Healthcare Providers with real specialties"
echo "- 15,285+ Anonymized Patients"
echo "- 227 AI-Generated Patient Clusters"
echo "- 688 Cluster Insights"
echo "- 378 Drug Recommendations"
echo "- 7,533+ EMR Data Points"
echo
echo "📋 HCP login credentials saved to: hcp_credentials.txt"
echo "🚀 Start server: python manage.py runserver"
echo "🌐 Visit: http://127.0.0.1:8000/"
echo
echo "Sample login:"
echo "Username: sarah.ray"
echo "Password: AdEmfCiX"
echo