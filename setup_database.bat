@echo off
echo ============================================
echo ProviderPulse Database Setup - Clustering Branch
echo ============================================
echo.

echo Step 1: Installing required packages...
pip install pandas requests faker
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)
echo ✅ Packages installed
echo.

echo Step 2: Setting up database...
python manage.py makemigrations
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Database setup failed
    pause
    exit /b 1
)
echo ✅ Database setup complete
echo.

echo Step 3: Downloading real healthcare data...
python download_emr_data.py
if %errorlevel% neq 0 (
    echo ERROR: Healthcare data download failed
    pause
    exit /b 1
)
echo ✅ Real healthcare data downloaded
echo.

echo Step 4: Populating with real EMR data...
python seed_real_emr.py
if %errorlevel% neq 0 (
    echo ERROR: EMR data population failed
    pause
    exit /b 1
)
echo ✅ EMR data populated
echo.

echo Step 5: Generating clustering features...
python seed_clustering.py
if %errorlevel% neq 0 (
    echo ERROR: Clustering features failed
    pause
    exit /b 1
)
echo ✅ Clustering features generated
echo.

echo Step 6: Creating HCP login accounts...
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
echo Your ProviderPulse database is now fully populated with:
echo - 50 Healthcare Providers with real specialties
echo - 15,285+ Anonymized Patients
echo - 227 AI-Generated Patient Clusters  
echo - 688 Cluster Insights
echo - 378 Drug Recommendations
echo - 7,533+ EMR Data Points
echo.
echo 📋 HCP login credentials saved to: hcp_credentials.txt
echo 🚀 Start server: python manage.py runserver
echo 🌐 Visit: http://127.0.0.1:8000/
echo.
echo Sample login:
echo Username: sarah.ray
echo Password: AdEmfCiX
echo.
pause