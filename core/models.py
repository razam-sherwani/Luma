
from django.db import models

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
