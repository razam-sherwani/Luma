@echo off
REM Pulse Complete Setup Script for Main Branch
REM Run this to get the exact same database as the main development environment

echo 🚀 Pulse Complete Setup Starting...
echo ================================================
echo.

echo 📦 Step 1: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

echo 🗄️ Step 2: Setting up database...
python manage.py makemigrations
python manage.py migrate
if %errorlevel% neq 0 (
    echo ❌ Database setup failed
    pause
    exit /b 1
)
echo ✅ Database initialized
echo.

echo 📥 Step 3: Downloading healthcare data...
python download_emr_data.py
if %errorlevel% neq 0 (
    echo ❌ Failed to download EMR data
    pause
    exit /b 1
)
echo ✅ Healthcare data downloaded
echo.

echo 🏥 Step 4: Creating healthcare providers...
python seed_real_emr.py
if %errorlevel% neq 0 (
    echo ❌ Failed to create HCP data
    pause
    exit /b 1
)
echo ✅ Healthcare providers created
echo.

echo 🧠 Step 5: Generating AI clustering features...
python seed_clustering.py
if %errorlevel% neq 0 (
    echo ❌ Failed to generate clustering data
    pause
    exit /b 1
)
echo ✅ AI clustering features generated
echo.

echo 🔐 Step 6: Creating login accounts...
python create_hcp_accounts.py
if %errorlevel% neq 0 (
    echo ERROR: HCP account creation failed
    pause
    exit /b 1
)
echo ✅ HCP login accounts created
echo.

echo ============================================
echo 🎉 SETUP COMPLETE!
echo ============================================
echo.
echo Your Pulse database is now fully populated with:
echo - 50 Healthcare Providers with real specialties
echo - 15,285+ Anonymized Patients
echo - 227 AI-Generated Patient Clusters  
echo - 688 Cluster Insights
echo - 378 Drug Recommendations
echo - 7,533+ EMR Data Points
echo.
echo 📋 HCP login credentials saved to: data/hcp_credentials.txt
echo 🚀 Start server: python manage.py runserver
echo 🌐 Visit: http://127.0.0.1:8000/
echo.
echo Sample login:
echo Username: sarah.ray
echo Password: AdEmfCiX
echo.
pause