from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('hcp/<int:hcp_id>/', views.hcp_profile, name='hcp_profile'),
]