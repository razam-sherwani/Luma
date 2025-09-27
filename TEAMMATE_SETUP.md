# 🚀 ProviderPulse Database Setup Guide - Clustering Branch

## Quick Setup for Teammates

Follow these steps to populate your database with the complete clustering features and data:

### **Prerequisites**
1. Make sure you're on the `clustering` branch
2. Python 3.8+ installed
3. Django dependencies installed

### **Step-by-Step Setup**

#### 1. **Install Required Packages**
```bash
pip install pandas requests faker
```

#### 2. **Setup Database**
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 3. **Download Real Healthcare Data**
```bash
python download_emr_data.py
```
*This downloads real CMS provider data and generates realistic medical conditions*

#### 4. **Populate with Real EMR Data** 
```bash
python seed_real_emr.py
```
*This creates 50 real healthcare providers with authentic specialties and medical data*

#### 5. **Generate Clustering Features**
```bash
python seed_clustering.py
```
*This adds 15,285 patients, AI clusters, insights, and drug recommendations*

#### 6. **Create HCP Login Accounts**
```bash
python create_hcp_accounts.py
```
*This creates login credentials for all 50 healthcare providers*

### **Final Result**
After running all scripts, you'll have:
- ✅ **50 Healthcare Providers** with real CMS specialties
- ✅ **15,285 Anonymized Patients** with realistic medical profiles  
- ✅ **227 AI-Generated Patient Clusters**
- ✅ **688 Cluster Insights** with treatment recommendations
- ✅ **378 Drug Recommendations** based on evidence
- ✅ **7,533 EMR Data Points** (labs, vitals, medications)
- ✅ **50 HCP Login Accounts** (credentials in `hcp_credentials.txt`)

### **Test the Platform**
1. Start server: `python manage.py runserver`
2. Visit: http://127.0.0.1:8000/
3. Login with HCP credentials from `hcp_credentials.txt`
4. Explore: `/dashboard/patients/` for patient database
5. View clusters: `/dashboard/cluster/<id>/` for AI insights

---

## **🔧 Troubleshooting**

### **If you get import errors:**
```bash
pip install django pandas requests faker
```

### **If migrations fail:**
```bash
python manage.py makemigrations core
python manage.py migrate
```

### **If scripts fail:**
Make sure you run them in this exact order - each script depends on the previous ones.

### **Script Dependencies:**
1. `download_emr_data.py` → Creates `emr_data/` folder
2. `seed_real_emr.py` → Uses `emr_data/` to create HCPs and cohorts  
3. `seed_clustering.py` → Uses existing HCPs to create patients and clusters
4. `create_hcp_accounts.py` → Uses existing HCPs to create login accounts

---

## **📁 Files You'll Get**

After setup completion:
- `emr_data/` - Real healthcare data CSVs
- `hcp_credentials.txt` - Login credentials for all HCPs
- `HCP_LOGIN_GUIDE.md` - Quick reference for testing
- `CLUSTERING_FEATURES.md` - Feature documentation

---

## **⚡ Quick Test**

Sample login to verify everything works:
- **Username:** `sarah.ray`
- **Password:** `AdEmfCiX` 
- **Role:** Internal Medicine HCP
- **Features:** 300+ patients, AI clusters, drug recommendations

---

**🎯 Total Setup Time:** ~5-10 minutes  
**🎉 Result:** Fully functional AI-powered healthcare platform with realistic data!