#!/bin/bash
# ProviderPulse Complete Setup Script for Main Branch
# Run this to get the exact same database as the main development environment

echo "🚀 ProviderPulse Complete Setup Starting..."
echo "================================================"

# Check if on main branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "unknown" ]; then
    echo "⚠️  WARNING: You're on branch '$BRANCH', not 'main'"
    echo "Switch to main branch with: git checkout main"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Step 1: Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo

echo "🗄️  Step 2: Setting up database..."
python manage.py makemigrations
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "❌ Database setup failed"
    exit 1
fi
echo "✅ Database initialized"
echo

echo "📥 Step 3: Downloading healthcare data..."
python download_emr_data.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to download EMR data"
    exit 1
fi
echo "✅ Healthcare data downloaded"
echo

echo "🏥 Step 4: Creating healthcare providers..."
python seed_real_emr.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to create HCP data"
    exit 1
fi
echo "✅ Healthcare providers created"
echo

echo "🧠 Step 5: Generating AI clustering features..."
python seed_clustering.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to generate clustering data"
    exit 1
fi
echo "✅ AI clustering features generated"
echo

echo "🔐 Step 6: Creating login accounts..."
python create_hcp_accounts.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to create HCP accounts"
    exit 1
fi
echo "✅ Login accounts created"
echo

echo "================================================"
echo "✅ SETUP COMPLETE!"
echo "================================================"
echo "🎉 Your database now matches the main dev environment!"
echo
echo "  • 688+ AI-Generated Cluster Insights"
echo "  • 378+ Evidence-Based Drug Recommendations"  
echo "  • 7,533+ EMR Data Points (labs, vitals, medications)"
echo "  • Complete patient clustering network"
echo
echo "📋 HCP login credentials: hcp_credentials.txt"
echo
echo "Next steps:"
echo "  1. Start server: python manage.py runserver"
echo "  2. Visit: http://127.0.0.1:8000/"
echo "  3. Test login with: sarah.ray / AdEmfCiX"
echo "  4. Explore AI features at: /dashboard/cohort-cluster-network/"
echo
echo "🔍 Verification:"
echo "  • Patient database should show 15,285+ patients"
echo "  • Network visualization should load without errors"
echo "  • All HCP logins should work from credentials file"
echo