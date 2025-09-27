
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('HCP', 'Healthcare Provider'),
        ('HCR', 'Healthcare Rep'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=3, choices=ROLE_CHOICES)
    specialty = models.CharField(max_length=100, blank=True)  # For HCPs
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class HCP(models.Model):
	name = models.CharField(max_length=100)
	specialty = models.CharField(max_length=100)
	contact_info = models.CharField(max_length=200)

	def __str__(self):
		return self.name

class ResearchUpdate(models.Model):
	headline = models.CharField(max_length=200)
	specialty = models.CharField(max_length=100)
	date = models.DateField()

	def __str__(self):
		return self.headline

class EMRData(models.Model):
	hcp = models.ForeignKey(HCP, on_delete=models.CASCADE)
	metric_name = models.CharField(max_length=100)
	value = models.CharField(max_length=100)
	date = models.DateField()

	def __str__(self):
		return f"{self.hcp.name} - {self.metric_name}: {self.value}"

class Engagement(models.Model):
	hcp = models.ForeignKey(HCP, on_delete=models.CASCADE)
	date = models.DateField()
	note = models.TextField()

	def __str__(self):
		return f"{self.hcp.name} - {self.date}"

class HCRRecommendation(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('LOW', 'Low Priority'),
    ]
    
    hcp_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    title = models.CharField(max_length=200)
    message = models.TextField()
    research_update = models.ForeignKey(ResearchUpdate, on_delete=models.CASCADE, null=True, blank=True)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='MEDIUM')
    created_date = models.DateField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Recommendation for {self.hcp_user.username}: {self.title}"

class PatientCohort(models.Model):
    """Represents a group of patients with similar conditions/symptoms"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    condition = models.CharField(max_length=100)  # e.g., "Type 2 Diabetes", "Hypertension"
    specialty = models.CharField(max_length=100)
    patient_count = models.IntegerField(default=0)
    created_date = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.patient_count} patients)"

class TreatmentOutcome(models.Model):
    """Tracks treatment effectiveness for patient cohorts"""
    cohort = models.ForeignKey(PatientCohort, on_delete=models.CASCADE, related_name='treatment_outcomes')
    treatment_name = models.CharField(max_length=200)
    success_rate = models.FloatField()  # Percentage of patients who responded well
    side_effects = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.treatment_name} for {self.cohort.name} ({self.success_rate}% success)"

class CohortRecommendation(models.Model):
    """Recommendations for HCPs based on patient cohort data"""
    PRIORITY_CHOICES = [
        ('HIGH', 'High Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('LOW', 'Low Priority'),
    ]
    
    hcp = models.ForeignKey(HCP, on_delete=models.CASCADE, related_name='cohort_recommendations')
    cohort = models.ForeignKey(PatientCohort, on_delete=models.CASCADE)
    treatment_outcome = models.ForeignKey(TreatmentOutcome, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='MEDIUM')
    created_date = models.DateField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Recommendation for {self.hcp.name}: {self.title}"

class ActionableInsight(models.Model):
    """High-priority insights for HCRs about HCP opportunities"""
    INSIGHT_TYPE_CHOICES = [
        ('MISSING_TREATMENT', 'Missing Standard-of-Care Treatment'),
        ('NEW_RESEARCH', 'New Research Highly Relevant'),
        ('PATIENT_COHORT', 'Patient Cohort Opportunity'),
        ('ENGAGEMENT_OVERDUE', 'Overdue Engagement'),
        ('TREATMENT_GAP', 'Treatment Gap Identified'),
    ]
    
    hcp = models.ForeignKey(HCP, on_delete=models.CASCADE, related_name='actionable_insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority_score = models.IntegerField(default=0)  # 0-100, higher = more important
    patient_impact = models.IntegerField(default=0)  # Estimated number of patients affected
    research_update = models.ForeignKey(ResearchUpdate, on_delete=models.CASCADE, null=True, blank=True)
    cohort = models.ForeignKey(PatientCohort, on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    is_addressed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_insight_type_display()}: {self.title}"