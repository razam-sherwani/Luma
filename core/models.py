
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
