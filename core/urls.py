from django.urls import path
from . import views, research_views

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
    path('upload-emr-patient/', views.upload_emr_patient, name='upload_emr_patient'),
    path('patient/<str:patient_id>/update/', views.update_patient, name='update_patient'),
    path('patient/<str:patient_id>/delete/', views.delete_patient, name='delete_patient'),
    path('cohort-cluster-network/', views.cohort_cluster_network, name='cohort_cluster_network'),
    # Research URLs
    path('research/', research_views.research_dashboard, name='research_dashboard'),
    path('research/<int:research_id>/', research_views.research_detail, name='research_detail'),
    path('api/research/by-specialty/', research_views.get_research_by_specialty, name='research_by_specialty'),
    path('api/research/update/', research_views.trigger_research_update, name='trigger_research_update'),
    # Intelligent Recommendation URLs
    path('hcp/<int:hcp_id>/create-recommendation/', views.create_recommendation, name='create_recommendation'),
    path('recommendation/<int:recommendation_id>/', views.view_recommendation, name='view_recommendation'),
    path('recommendation/<int:recommendation_id>/edit/', views.edit_recommendation, name='edit_recommendation'),
    path('recommendation/<int:recommendation_id>/delete/', views.delete_recommendation, name='delete_recommendation'),
    path('recommendation/<int:recommendation_id>/send/', views.send_recommendation_message, name='send_recommendation_message'),
    path('hcr-recommendations/', views.hcr_recommendations, name='hcr_recommendations'),
    # New recommendation generation URLs
    path('generate-recommendation/', views.generate_recommendation_page, name='generate_recommendation_page'),
    path('hcp/<int:hcp_id>/create-recommendation-ajax/', views.create_recommendation_ajax, name='create_recommendation_ajax'),
    # Recommendation action URLs
    path('mark-recommendation-read/<int:recommendation_id>/', views.mark_recommendation_read, name='mark_recommendation_read_ajax'),
    path('accept-recommendation/<int:recommendation_id>/', views.accept_recommendation, name='accept_recommendation'),
    path('decline-recommendation/<int:recommendation_id>/', views.decline_recommendation, name='decline_recommendation'),
    path('get-recommendation-research/<int:recommendation_id>/', views.get_recommendation_research, name='get_recommendation_research'),
]