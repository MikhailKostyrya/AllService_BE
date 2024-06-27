from django.urls import path
from .views import RecommendationView

urlpatterns = [
    path('recommend/<int:user_id>/', RecommendationView.as_view(), name='recommend_services'),
]
