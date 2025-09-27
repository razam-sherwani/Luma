from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('hcp/<int:hcp_id>/', views.hcp_profile, name='hcp_profile'),
    path('recommendation/<int:recommendation_id>/read/', views.mark_recommendation_read, name='mark_recommendation_read'),
    path('insight/<int:insight_id>/addressed/', views.mark_insight_addressed, name='mark_insight_addressed'),
    path('drug-recommendation/<int:recommendation_id>/reviewed/', views.mark_recommendation_reviewed, name='mark_recommendation_reviewed'),
    path('patients/', views.patient_database, name='patient_database'),
    path('patient/<str:patient_id>/', views.patient_detail, name='patient_detail'),
    path('cluster/<int:cluster_id>/', views.cluster_detail, name='cluster_detail'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('cohort-cluster-network/', views.cohort_cluster_network, name='cohort_cluster_network'),
    path('ai-cohort-identification/', views.ai_cohort_identification, name='ai_cohort_identification'),
]