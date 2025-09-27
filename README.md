# ProviderPulse - The Intelligent Engagement Platform

ProviderPulse is an intelligent dashboard that acts as a co-pilot for healthcare engagement managers. By simulating insights from Electronic Medical Records (EMRs) and tracking the latest medical research, the platform generates prioritized, actionable alerts to help healthcare reps know exactly who to contact, what to talk about, and why it's critically relevant today.

## Features

- **Smart Dashboard**: View overdue engagements, new research alerts, and EMR flags in one place
- **HCP Profile Management**: Detailed healthcare provider profiles with engagement history
- **Research Tracking**: Stay updated with the latest medical research by specialty
- **EMR Insights**: Monitor patient volume changes and key metrics
- **Engagement Logging**: Easy-to-use forms for tracking interactions with HCPs

## Quick Setup

### Prerequisites

- Python 3.8 or higher
- Django 5.0
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/razam-sherwani/ProviderPulse.git
   cd ProviderPulse
   ```

2. **Install dependencies** (optional: use virtual environment)
   ```bash
   # Create virtual environment (recommended)
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   
   # Install Django (if not already installed)
   pip install django
   ```

3. **Set up the database**
   ```bash
   # Create and apply migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Load dummy data into the database**
   ```bash
   # Run the seed script to populate the database with sample data
   python seed.py
   ```
   
   This will create:
   - 5 sample Healthcare Providers (HCPs) with different specialties
   - Research updates relevant to each specialty
   - EMR data with metrics like patient volume and top diagnoses
   - Sample engagement history for each HCP

5. **Create a superuser** (optional, for admin access)
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Sign up for a new account or log in
   - Explore the dashboard with the pre-loaded sample data

## Sample Data Overview

The `seed.py` script creates the following sample data:

### Healthcare Providers (HCPs)
- **Dr. Alice Smith** - Oncology
- **Dr. Bob Jones** - Cardiology  
- **Dr. Carol Lee** - Endocrinology
- **Dr. David Kim** - Neurology
- **Dr. Eva Patel** - Pediatrics

### Research Updates
- Immunotherapy advances in oncology
- Cardiac stent technology breakthroughs
- Diabetes management guidelines
- Pediatric vaccine developments
- Migraine treatment innovations

### EMR Data
- Patient volume trends (Increased/Stable/Decreased)
- Top diagnoses by specialty
- Recent metric changes with timestamps

### Engagement History
- Sample interaction notes for each HCP
- Varied engagement dates to demonstrate overdue alerts
- Different types of contact methods (calls, emails, meetings)

## Usage

1. **Landing Page**: Visit the homepage to learn about ProviderPulse
2. **Sign Up/Login**: Create an account or sign in to access your dashboard
3. **Dashboard**: View three key sections:
   - **Overdue Engagements**: HCPs not contacted in 30+ days
   - **New Research Alerts**: Latest studies by specialty
   - **EMR Flags**: Recent data changes and patient metrics
4. **HCP Profiles**: Click on any HCP name to view:
   - Contact information and specialty
   - Relevant research updates
   - EMR data and trends
   - Complete engagement history
   - Form to log new interactions

## Project Structure

```
ProviderPulse/
├── core/                   # Main app with models and dashboard views
├── landing/                # Landing page app
├── accounts/               # User authentication app
├── templates/              # HTML templates
├── seed.py                 # Database seeding script
├── manage.py              # Django management script
└── providerpulse/         # Project settings
```

## Resetting the Database

If you want to reset the database and reload fresh dummy data:

```bash
# Delete the database file (SQLite)
rm db.sqlite3  # On Windows: del db.sqlite3

# Recreate the database
python manage.py migrate

# Reload dummy data
python seed.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of a hackathon MVP demonstration.