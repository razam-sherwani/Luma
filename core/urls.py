from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('hcp/<int:hcp_id>/', views.hcp_profile, name='hcp_profile'),
    path('recommendation/<int:recommendation_id>/read/', views.mark_recommendation_read, name='mark_recommendation_read'),
]