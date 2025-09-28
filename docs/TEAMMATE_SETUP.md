# 🚀 Pulse Database Setup Guide - Main Branch

## Complete Setup for Teammates

Follow these steps exactly to get the same database and clustering features as the main development environment:

### **Prerequisites**
1. Make sure you're on the `main` branch
2. Python 3.8+ installed
3. Git repository cloned

### **Step-by-Step Setup**

#### 1. **Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt
```

#### 2. **Initialize Database**
```bash
# Create fresh database
python manage.py makemigrations
python manage.py migrate
```

#### 3. **Run Complete Data Setup**
Run these scripts in **EXACT ORDER** (each depends on the previous):

```bash
# Step 1: Download real healthcare provider data
python download_emr_data.py
```
*Downloads CMS provider data and medical conditions (~2 minutes)*

```bash
# Step 2: Create healthcare providers and basic data
python seed_real_emr.py  
```
*Creates 50 real HCPs with authentic specialties (~1 minute)*

```bash  
# Step 3: Generate AI clustering features and patients
python seed_clustering.py
```
*Adds 15,285 patients, clusters, and AI insights (~3-5 minutes)*

```bash
# Step 4: Create login accounts for all HCPs
python create_hcp_accounts.py
```
*Generates login credentials for all providers (~30 seconds)*

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
1. **Start server:** `python manage.py runserver`
2. **Visit:** http://127.0.0.1:8000/
3. **Login:** Use credentials from `hcp_credentials.txt`
4. **Explore Features:**
   - Patient Database: `/dashboard/patients/`
   - AI Clustering Network: `/dashboard/cohort-cluster-network/` 
   - Individual Clusters: Click any cluster to view AI insights
   - Patient Details: Click any patient for full medical profile

---

## **🔧 Troubleshooting**

### **If you get import errors:**
```bash
pip install -r requirements.txt
```

### **If migrations fail:**
```bash
python manage.py makemigrations core
python manage.py makemigrations accounts  
python manage.py migrate
```

### **If scripts get interrupted:**
You can safely re-run any script - they handle duplicates gracefully.

### **CRITICAL: Script Order Matters**
**⚠️ MUST run in this order:**
1. `download_emr_data.py` → Downloads real healthcare data
2. `seed_real_emr.py` → Creates HCP profiles and cohorts  
3. `seed_clustering.py` → Generates patients and AI clustering
4. `create_hcp_accounts.py` → Creates login accounts

**❌ Common Mistakes:**
- Skipping `download_emr_data.py` → Other scripts will fail
- Running scripts out of order → Database relationships break
- Not waiting for scripts to complete → Incomplete data

### **Database Issues:**
If your database gets corrupted or incomplete:
```bash
# Nuclear option - fresh start
rm db.sqlite3
python manage.py migrate
# Then re-run all 4 scripts in order
```

---

## **📁 Files You'll Get**

After setup completion:
- `emr_data/` - Real healthcare data CSVs
- `hcp_credentials.txt` - Login credentials for all HCPs
- `HCP_LOGIN_GUIDE.md` - Quick reference for testing
- `CLUSTERING_FEATURES.md` - Feature documentation

---

## **⚡ Quick Verification**

**Test login to confirm setup worked:**
- **Username:** `sarah.ray`
- **Password:** `AdEmfCiX` 
- **Role:** Internal Medicine HCP
- **Expected:** 300+ patients, AI clusters, treatment insights

**Full verification checklist:**
- [ ] Can login with HCP credentials
- [ ] Patient database shows 15,285 patients  
- [ ] Cohort-cluster network loads without errors
- [ ] Individual patient profiles show outcomes and EMR data
- [ ] Cluster insights display AI recommendations

---

## **� Getting Help**

**If setup fails:**
1. Check you're on `main` branch: `git branch`
2. Verify all 4 scripts completed successfully
3. Check `hcp_credentials.txt` exists with 50+ accounts
4. Confirm database has data: login and check patient count

**Expected final state:**
- 50 HCP accounts with working logins
- 15,285+ anonymized patients 
- 227+ AI-generated clusters
- Working network visualization
- Complete EMR data points

---

**🎯 Total Setup Time:** ~7-12 minutes  
**🎉 Result:** Identical database to main dev environment!