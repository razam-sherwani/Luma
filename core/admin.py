from django.contrib import admin
from .models import (HCP, ResearchUpdate, EMRData, Engagement, UserProfile, HCRRecommendation, 
                    PatientCohort, TreatmentOutcome, CohortRecommendation, ActionableInsight,
                    AnonymizedPatient, EMRDataPoint, PatientOutcome, PatientCluster, 
                    ClusterMembership, ClusterInsight, DrugRecommendation)

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

@admin.register(AnonymizedPatient)
class AnonymizedPatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'hcp', 'primary_diagnosis', 'age_group', 'gender', 'last_visit_date']
    list_filter = ['hcp__specialty', 'age_group', 'gender', 'race', 'primary_diagnosis']
    search_fields = ['patient_id', 'hcp__name', 'primary_diagnosis']
    readonly_fields = ['created_date', 'last_updated']

@admin.register(EMRDataPoint)
class EMRDataPointAdmin(admin.ModelAdmin):
    list_display = ['patient', 'data_type', 'metric_name', 'value', 'date_recorded', 'is_abnormal']
    list_filter = ['data_type', 'is_abnormal', 'date_recorded', 'patient__hcp__specialty']
    search_fields = ['patient__patient_id', 'metric_name', 'value']

@admin.register(PatientOutcome)
class PatientOutcomeAdmin(admin.ModelAdmin):
    list_display = ['patient', 'treatment', 'outcome', 'outcome_date', 'duration_months']
    list_filter = ['outcome', 'outcome_date', 'patient__hcp__specialty']
    search_fields = ['patient__patient_id', 'treatment']

@admin.register(PatientCluster)
class PatientClusterAdmin(admin.ModelAdmin):
    list_display = ['name', 'hcp', 'cluster_type', 'patient_count', 'success_rate', 'created_date']
    list_filter = ['cluster_type', 'hcp__specialty', 'created_date']
    search_fields = ['name', 'hcp__name', 'primary_diagnosis']

@admin.register(ClusterMembership)
class ClusterMembershipAdmin(admin.ModelAdmin):
    list_display = ['patient', 'cluster', 'similarity_score', 'assigned_date']
    list_filter = ['cluster__cluster_type', 'assigned_date', 'patient__hcp__specialty']
    search_fields = ['patient__patient_id', 'cluster__name']

@admin.register(ClusterInsight)
class ClusterInsightAdmin(admin.ModelAdmin):
    list_display = ['cluster', 'insight_type', 'title', 'confidence_score', 'created_date', 'is_implemented']
    list_filter = ['insight_type', 'confidence_score', 'created_date', 'is_implemented', 'cluster__hcp__specialty']
    search_fields = ['cluster__name', 'title', 'description']

@admin.register(DrugRecommendation)
class DrugRecommendationAdmin(admin.ModelAdmin):
    list_display = ['hcp', 'drug_name', 'indication', 'success_rate', 'evidence_level', 'priority', 'created_date', 'is_reviewed']
    list_filter = ['priority', 'evidence_level', 'created_date', 'is_reviewed', 'hcp__specialty']
    search_fields = ['hcp__name', 'drug_name', 'indication']
