from django.contrib import admin
from .models import HCP, ResearchUpdate, EMRData, Engagement, UserProfile, HCRRecommendation, PatientCohort, TreatmentOutcome, CohortRecommendation, ActionableInsight

@admin.register(HCP)
class HCPAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'contact_info']
    list_filter = ['specialty']
    search_fields = ['name', 'specialty']

@admin.register(ResearchUpdate)
class ResearchUpdateAdmin(admin.ModelAdmin):
    list_display = ['headline', 'specialty', 'date']
    list_filter = ['specialty', 'date']
    search_fields = ['headline', 'specialty']

@admin.register(EMRData)
class EMRDataAdmin(admin.ModelAdmin):
    list_display = ['hcp', 'metric_name', 'value', 'date']
    list_filter = ['metric_name', 'date', 'hcp__specialty']
    search_fields = ['hcp__name', 'metric_name']

@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ['hcp', 'date', 'note']
    list_filter = ['date', 'hcp__specialty']
    search_fields = ['hcp__name', 'note']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'specialty']
    list_filter = ['role', 'specialty']
    search_fields = ['user__username', 'specialty']

@admin.register(HCRRecommendation)
class HCRRecommendationAdmin(admin.ModelAdmin):
    list_display = ['hcp_user', 'title', 'priority', 'created_date', 'is_read']
    list_filter = ['priority', 'created_date', 'is_read']
    search_fields = ['hcp_user__username', 'title']

@admin.register(PatientCohort)
class PatientCohortAdmin(admin.ModelAdmin):
    list_display = ['name', 'condition', 'specialty', 'patient_count', 'created_date']
    list_filter = ['specialty', 'condition', 'created_date']
    search_fields = ['name', 'condition', 'specialty']

@admin.register(TreatmentOutcome)
class TreatmentOutcomeAdmin(admin.ModelAdmin):
    list_display = ['cohort', 'treatment_name', 'success_rate', 'created_date']
    list_filter = ['cohort__specialty', 'success_rate', 'created_date']
    search_fields = ['cohort__name', 'treatment_name']

@admin.register(CohortRecommendation)
class CohortRecommendationAdmin(admin.ModelAdmin):
    list_display = ['hcp', 'cohort', 'title', 'priority', 'created_date', 'is_read']
    list_filter = ['priority', 'created_date', 'is_read', 'hcp__specialty']
    search_fields = ['hcp__name', 'cohort__name', 'title']

@admin.register(ActionableInsight)
class ActionableInsightAdmin(admin.ModelAdmin):
    list_display = ['hcp', 'insight_type', 'title', 'priority_score', 'patient_impact', 'created_date', 'is_addressed']
    list_filter = ['insight_type', 'priority_score', 'created_date', 'is_addressed', 'hcp__specialty']
    search_fields = ['hcp__name', 'title', 'description']
