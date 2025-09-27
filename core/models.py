
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

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
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.name

class ResearchUpdate(models.Model):
	headline = models.CharField(max_length=200)
	specialty = models.CharField(max_length=100)
	date = models.DateField()
	abstract = models.TextField(blank=True, null=True)
	source = models.CharField(max_length=100, default='Manual')
	relevance_score = models.FloatField(default=0.0)  # AI-calculated relevance
	is_high_impact = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-date', '-relevance_score']
		indexes = [
			models.Index(fields=['specialty', '-date']),
			models.Index(fields=['date']),
			models.Index(fields=['-relevance_score']),
		]

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

class AnonymizedPatient(models.Model):
    """Individual patient records - anonymized for HIPAA compliance"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Unknown'),
    ]
    
    RACE_CHOICES = [
        ('WHITE', 'White'),
        ('BLACK', 'Black or African American'),
        ('ASIAN', 'Asian'),
        ('NATIVE', 'American Indian or Alaska Native'),
        ('PACIFIC', 'Native Hawaiian or Other Pacific Islander'),
        ('OTHER', 'Other'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    ETHNICITY_CHOICES = [
        ('HISPANIC', 'Hispanic or Latino'),
        ('NON_HISPANIC', 'Not Hispanic or Latino'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    patient_id = models.CharField(max_length=50, unique=True)
    hcp = models.ForeignKey(HCP, on_delete=models.CASCADE, related_name='patients')
    age_group = models.CharField(max_length=20)  # e.g., "18-25", "26-35", etc.
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    race = models.CharField(max_length=10, choices=RACE_CHOICES)
    ethnicity = models.CharField(max_length=15, choices=ETHNICITY_CHOICES)
    zip_code_prefix = models.CharField(max_length=5)  # First 5 digits only
    primary_diagnosis = models.CharField(max_length=200)
    secondary_diagnoses = models.TextField(blank=True)
    comorbidities = models.TextField(blank=True)
    current_treatments = models.TextField(blank=True)
    treatment_history = models.TextField(blank=True)
    medication_adherence = models.CharField(max_length=20, blank=True)
    last_lab_values = models.JSONField(default=dict, blank=True)
    vital_signs = models.JSONField(default=dict, blank=True)
    last_visit_date = models.DateField()
    visit_frequency = models.CharField(max_length=20)
    emergency_visits_6m = models.IntegerField(default=0)
    hospitalizations_6m = models.IntegerField(default=0)
    risk_factors = models.TextField(blank=True)
    family_history = models.TextField(blank=True)
    insurance_type = models.CharField(max_length=50, blank=True)
    medication_access = models.CharField(max_length=20, blank=True)
    created_date = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"Patient {self.patient_id} - {self.primary_diagnosis}"

class EMRDataPoint(models.Model):
    """Individual EMR data points for each patient"""
    DATA_TYPE_CHOICES = [
        ('LAB_RESULT', 'Lab Result'),
        ('VITAL_SIGN', 'Vital Sign'),
        ('DIAGNOSIS', 'Diagnosis'),
        ('MEDICATION', 'Medication'),
        ('PROCEDURE', 'Procedure'),
        ('SYMPTOM', 'Symptom'),
        ('RISK_FACTOR', 'Risk Factor'),
    ]
    
    patient = models.ForeignKey(AnonymizedPatient, on_delete=models.CASCADE, related_name='data_points')
    data_type = models.CharField(max_length=15, choices=DATA_TYPE_CHOICES)
    metric_name = models.CharField(max_length=100)
    value = models.CharField(max_length=200)
    unit = models.CharField(max_length=50, blank=True)
    date_recorded = models.DateField()
    is_abnormal = models.BooleanField(default=False)
    severity = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.metric_name}: {self.value}"

class PatientOutcome(models.Model):
    """Treatment outcomes for individual patients"""
    OUTCOME_CHOICES = [
        ('IMPROVED', 'Improved'),
        ('STABLE', 'Stable'),
        ('DETERIORATED', 'Deteriorated'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    patient = models.ForeignKey(AnonymizedPatient, on_delete=models.CASCADE, related_name='outcomes')
    treatment = models.CharField(max_length=200)
    outcome = models.CharField(max_length=15, choices=OUTCOME_CHOICES)
    outcome_date = models.DateField()
    notes = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    duration_months = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.treatment}: {self.outcome}"

class PatientCluster(models.Model):
    """AI-driven patient clustering for similarity analysis"""
    CLUSTER_TYPE_CHOICES = [
        ('DIAGNOSIS', 'Diagnosis-Based'),
        ('TREATMENT_RESPONSE', 'Treatment Response'),
        ('RISK_PROFILE', 'Risk Profile'),
        ('DEMOGRAPHIC', 'Demographic'),
        ('CLINICAL', 'Clinical Metrics'),
    ]
    
    hcp = models.ForeignKey(HCP, on_delete=models.CASCADE, related_name='patient_clusters')
    name = models.CharField(max_length=200)
    cluster_type = models.CharField(max_length=20, choices=CLUSTER_TYPE_CHOICES)
    description = models.TextField()
    patient_count = models.IntegerField(default=0)
    avg_risk_score = models.FloatField(default=0.0)
    primary_diagnosis = models.CharField(max_length=200, blank=True)
    common_treatments = models.TextField(blank=True)
    success_rate = models.FloatField(default=0.0)
    cluster_center = models.JSONField(default=dict)
    features_used = models.JSONField(default=list)
    created_date = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.patient_count} patients)"

class ClusterMembership(models.Model):
    """Links patients to clusters with similarity scores"""
    patient = models.ForeignKey(AnonymizedPatient, on_delete=models.CASCADE, related_name='cluster_memberships')
    cluster = models.ForeignKey(PatientCluster, on_delete=models.CASCADE, related_name='patients')
    similarity_score = models.FloatField(default=0.0)
    assigned_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('patient', 'cluster')
    
    def __str__(self):
        return f"{self.patient.patient_id} in {self.cluster.name} ({self.similarity_score:.2f})"

class ClusterInsight(models.Model):
    """AI-generated insights from patient clusters"""
    INSIGHT_TYPE_CHOICES = [
        ('TREATMENT_EFFECTIVENESS', 'Treatment Effectiveness'),
        ('PATTERN_DISCOVERY', 'Pattern Discovery'),
        ('RISK_FACTORS', 'Risk Factors'),
        ('TREATMENT_GAPS', 'Treatment Gaps'),
        ('OPTIMIZATION_OPPORTUNITY', 'Optimization Opportunity'),
    ]
    
    cluster = models.ForeignKey(PatientCluster, on_delete=models.CASCADE, related_name='insights')
    insight_type = models.CharField(max_length=25, choices=INSIGHT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    confidence_score = models.FloatField(default=0.0)
    actionable_recommendations = models.TextField()
    supporting_data = models.JSONField(default=dict)
    created_date = models.DateField(auto_now_add=True)
    is_implemented = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.cluster.name}: {self.title}"

class DrugRecommendation(models.Model):
    """Drug recommendations based on cluster analysis and research"""
    PRIORITY_CHOICES = [
        ('HIGH', 'High Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('LOW', 'Low Priority'),
    ]
    
    hcp = models.ForeignKey(HCP, on_delete=models.CASCADE, related_name='drug_recommendations')
    cluster = models.ForeignKey(PatientCluster, on_delete=models.CASCADE, null=True, blank=True)
    drug_name = models.CharField(max_length=200)
    indication = models.CharField(max_length=200)
    success_rate = models.FloatField()  # Based on cluster analysis
    patient_count = models.IntegerField()  # Number of similar patients
    evidence_level = models.CharField(max_length=20)  # e.g., "High", "Moderate", "Low"
    research_support = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    dosage_recommendations = models.TextField(blank=True)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='MEDIUM')
    created_date = models.DateField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.drug_name} for {self.hcp.name} - {self.success_rate}% success"


# New models for the research and messaging system

class PatientIssueAnalysis(models.Model):
    """Analysis of common issues across a doctor's patients"""
    hcp = models.ForeignKey(HCP, on_delete=models.CASCADE, related_name='issue_analyses')
    analysis_date = models.DateTimeField(auto_now_add=True)
    total_patients_analyzed = models.IntegerField()
    common_issues = models.JSONField()  # List of common issues with frequencies
    top_diagnoses = models.JSONField()  # Most frequent diagnoses
    treatment_gaps = models.JSONField()  # Areas where treatments might be missing
    risk_factors = models.JSONField()  # Common risk factors
    analysis_summary = models.TextField()
    
    class Meta:
        ordering = ['-analysis_date']
    
    def __str__(self):
        return f"Issue Analysis for {self.hcp.name} - {self.analysis_date.strftime('%Y-%m-%d')}"


class ScrapedResearch(models.Model):
    """Research articles scraped from medical databases"""
    title = models.CharField(max_length=500)
    authors = models.TextField(blank=True)
    journal = models.CharField(max_length=200, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    abstract = models.TextField()
    keywords = models.JSONField(default=list)  # List of keywords
    specialties = models.JSONField(default=list)  # Relevant specialties
    conditions_mentioned = models.JSONField(default=list)  # Medical conditions mentioned
    treatments_mentioned = models.JSONField(default=list)  # Treatments mentioned
    source_url = models.URLField(blank=True)
    source_database = models.CharField(max_length=100, default='PubMed')
    relevance_score = models.FloatField(default=0.0)  # AI-calculated relevance
    scraped_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-relevance_score', '-publication_date']
        indexes = [
            models.Index(fields=['-relevance_score']),
            models.Index(fields=['publication_date']),
        ]
    
    def __str__(self):
        return self.title


class IntelligentRecommendation(models.Model):
    """Combined recommendations based on patient analysis and research"""
    PRIORITY_CHOICES = [
        ('HIGH', 'High Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('LOW', 'Low Priority'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('VIEWED', 'Viewed'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    ]
    
    hcp = models.ForeignKey(HCP, on_delete=models.CASCADE, related_name='intelligent_recommendations')
    hcr_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_recommendations')
    patient_analysis = models.ForeignKey(PatientIssueAnalysis, on_delete=models.CASCADE)
    relevant_research = models.ManyToManyField(ScrapedResearch, blank=True)
    cluster_insights = models.ForeignKey(PatientCluster, on_delete=models.CASCADE, null=True, blank=True)
    
    recommendation_title = models.CharField(max_length=200)
    recommendation_summary = models.TextField()
    evidence_summary = models.TextField()  # Combined evidence from all sources
    patient_data_evidence = models.JSONField()  # Specific patient data supporting the recommendation
    research_evidence = models.JSONField()  # Research articles supporting the recommendation
    cluster_evidence = models.JSONField()  # Cluster analysis evidence
    
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    
    created_date = models.DateTimeField(auto_now_add=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    viewed_date = models.DateTimeField(null=True, blank=True)
    response_date = models.DateTimeField(null=True, blank=True)
    hcp_response = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.recommendation_title} for {self.hcp.name}"


class HCRMessage(models.Model):
    """Messages between HCRs and HCPs"""
    MESSAGE_TYPES = [
        ('RECOMMENDATION', 'Recommendation'),
        ('GENERAL', 'General Message'),
        ('FOLLOW_UP', 'Follow-up'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient_hcp = models.ForeignKey(HCP, on_delete=models.CASCADE, related_name='received_messages')
    message_type = models.CharField(max_length=15, choices=MESSAGE_TYPES, default='GENERAL')
    subject = models.CharField(max_length=200)
    message_content = models.TextField()
    recommendation = models.ForeignKey(IntelligentRecommendation, on_delete=models.CASCADE, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    read_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.subject} - {self.sender.username} to {self.recipient_hcp.name}"


class RecommendationFeedback(models.Model):
    """Feedback from HCPs on recommendations"""
    recommendation = models.OneToOneField(IntelligentRecommendation, on_delete=models.CASCADE, related_name='feedback')
    hcp = models.ForeignKey(HCP, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 star rating
    feedback_text = models.TextField(blank=True)
    was_helpful = models.BooleanField()
    will_implement = models.BooleanField()
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for {self.recommendation.recommendation_title} - {self.rating} stars"