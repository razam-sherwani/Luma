# 🔑 Quick Login Reference - Pulse HCP Accounts

## Sample HCP Login Credentials

Here are some sample HCP accounts you can use to test different specialties and features:

### 🏥 **Cardiology**
- **Username:** `sarah.ray`
- **Password:** `AdEmfCiX`
- **Specialty:** Internal Medicine
- **Patients:** ~300 with cardiovascular conditions

### 🧬 **Oncology** 
- **Username:** `lisa.smith`
- **Password:** `eSLy1XMz`
- **Specialty:** Internal Medicine
- **Patients:** ~250 with cancer diagnoses

### 💉 **Anesthesiology**
- **Username:** `corey.harvey`
- **Password:** `Bkg3N47y`
- **Specialty:** Anesthesiology
- **Patients:** ~200 surgical patients

### 🔬 **General Surgery**
- **Username:** `peter.richards`
- **Password:** `ePmDWxdh`
- **Specialty:** General Surgery
- **Patients:** ~280 surgical cases

### 👶 **Obstetrics/Gynecology**
- **Username:** `shannon.harris`
- **Password:** `2A7VzUBN`
- **Specialty:** Obstetrics/Gynecology
- **Patients:** ~320 women's health patients

---

## 🚀 How to Test HCP Features

1. **Login:** Go to http://127.0.0.1:8000/accounts/login/
2. **Use any credentials** from the list above
3. **Explore HCP Dashboard:** You'll see the HCP-specific view with:
   - Your assigned patients
   - AI-generated clusters for your patient population
   - Drug recommendations based on your specialty
   - Clinical insights specific to your practice

## 🔍 What Each HCP Will See

### **Patient Database** (`/dashboard/patients/`)
- Only patients assigned to that specific HCP
- Filtered by their specialty area
- Complete medical records for their patient population

### **Patient Clusters** (`/dashboard/cluster/<id>/`)
- AI-generated clusters of their similar patients
- Cluster insights specific to their practice patterns
- Treatment effectiveness analysis for their patient outcomes

### **Drug Recommendations**
- Personalized recommendations based on their patient clusters
- Evidence-based suggestions for their specialty area
- Success rates calculated from their similar patient populations

### **Cohort-Cluster Network** (`/dashboard/cohort-cluster-network/`)
- Interactive visualization of their patient relationships
- Network analysis of their specific patient clusters
- Filtering options relevant to their practice

---

## 📋 Complete Credentials List

For all 50 HCP login credentials, see: `hcp_credentials.txt`

**Specialties Available:**
- Internal Medicine
- Anesthesiology  
- General Surgery
- Obstetrics/Gynecology
- Hospitalist
- Cardiovascular Disease (Cardiology)
- Radiation Oncology
- Family Practice
- Infectious Disease
- Orthopedic Surgery
- Pain Management
- Urology
- Physical Medicine & Rehabilitation
- And many more...

---

## 🎯 Testing Scenarios

1. **Compare Specialties:** Login as different specialists to see how the AI clusters patients differently
2. **Drug Recommendations:** See how recommendations vary by specialty and patient population
3. **Cluster Analysis:** Compare cluster insights between high-volume vs. lower-volume providers
4. **Patient Outcomes:** Review how treatment success rates differ across provider types

---

**🔒 Security Note:** All passwords are randomly generated. You can change them through the Django admin interface if needed.

**📊 Data Note:** Each HCP has 200-400 realistic patients with specialty-appropriate conditions and treatments.