# Pulse - The Intelligent Engagement Platform

Pulse is an intelligent dashboard that acts as a co-pilot for healthcare engagement managers. By simulating insights from Electronic Medical Records (EMRs) and tracking the latest medical research, the platform generates prioritized, actionable alerts to help healthcare reps know exactly who to contact, what to talk about, and why it's critically relevant today.

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
   git clone https://github.com/razam-sherwani/Pulse.git
   cd Pulse
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

3. **Install Node.js dependencies for Tailwind CSS**
   ```bash
   # Install Node.js packages
   npm install
   
   # Build Tailwind CSS
   npm run build-css
   
   # For development with auto-rebuild:
   npm run watch-css
   ```

4. **Set up the database**
   ```bash
   # Create and apply migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Load realistic EMR data into the database** (RECOMMENDED)
   ```bash
   # First install required packages for data processing
   pip install pandas requests faker
   
   # Download real healthcare data from CMS and generate realistic EMR dataset
   python download_emr_data.py
   
   # Populate your database with real EMR data
   python seed_real_emr.py
   ```
   
   This will create realistic data based on **real CMS provider data**:
   - 50 Healthcare Providers from real CMS database with authentic specialties
   - 15 Patient Cohorts with real medical conditions (ICD-10 codes)
   - 228 EMR Records with realistic patient volumes and outcomes
   - 40 Treatment Outcomes with evidence-based success rates
   - 10 Research Updates based on current medical literature
   - 98 HCP-Cohort relationships based on specialty alignment
   - 50 Actionable Insights for clinical decision support
   
   **OR load basic sample data** (alternative):
   ```bash
   # Run the basic seed script for simple test data
   python seed.py
   ```

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

### Patient Cohorts & Network Data
- **15+ Patient Cohorts** across different medical conditions
- **Treatment Outcomes** with success rates and effectiveness data
- **HCP-Cohort Relationships** showing treatment patterns
- **Actionable Insights** for healthcare reps
- **Network Connections** demonstrating influence patterns

## Usage

1. **Landing Page**: Visit the homepage to learn about Pulse
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
5. **Network Visualization**: Access the interactive network view to:
   - Visualize HCP-patient cohort relationships
   - Identify high-priority engagement opportunities
   - Filter networks by condition, specialty, or region
   - Analyze treatment patterns and success rates

## UI & Styling

Pulse uses **Tailwind CSS 3.4.0** for modern, responsive design with beautiful glassmorphism effects and gradient styling.

### Development Workflow

```bash
# Install dependencies
npm install

# Development mode (auto-rebuild CSS on changes)
npm run watch-css

# Production build (optimized CSS)
npm run build-css

# Run Django development server
python manage.py runserver
```

### Design Features

- **🎨 Glassmorphism UI**: Modern frosted glass effects with backdrop blur
- **📱 Mobile-First**: Responsive design that works on all device sizes
- **🌈 Gradient Elements**: Beautiful color gradients throughout the interface
- **⚡ Smooth Animations**: Hover effects, transitions, and micro-interactions
- **🎯 Accessible**: Keyboard navigation and proper contrast ratios
- **💎 Modern Cards**: Elegant card-based layouts with hover transforms

### Custom Styling

The platform includes custom CSS components defined in `static/css/input.css`:
- Glass-morphism cards and navigation
- Gradient buttons and badges
- Enhanced form controls
- Floating animations
- Beautiful alert messages

### Tailwind Configuration

Custom configuration in `tailwind.config.js` includes:
- Pulse brand colors
- Custom gradient utilities
- Enhanced animation keyframes
- Typography scale optimization

## Project Structure

```
Pulse/
├── core/                   # Main app with models and dashboard views
├── landing/                # Landing page app
├── accounts/               # User authentication app
├── templates/              # HTML templates
├── seed.py                 # Database seeding script
├── manage.py              # Django management script
└── Pulse/         # Project settings
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