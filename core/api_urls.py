from django.urls import path
from . import api_views

urlpatterns = [
    path('cluster-network-data/', api_views.cluster_network_data, name='cluster_network_data'),
    path('cluster-recommendations/<int:cluster_id>/', api_views.cluster_recommendations, name='cluster_recommendations'),
    path('cluster-evidence/<int:cluster_id>/', api_views.cluster_evidence, name='cluster_evidence'),
]
