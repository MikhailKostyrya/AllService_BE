from django.urls import path
from .views import ServiceCreateAPIView, ServiceUpdateAPIView, ServiceDeleteAPIView

urlpatterns = [
    path('services/create/', ServiceCreateAPIView.as_view(), name='service_create'),
    path('services/<int:pk>/update/', ServiceUpdateAPIView.as_view(), name='service_update'),
    path('services/<int:pk>/delete/', ServiceDeleteAPIView.as_view(), name='service_delete'),
]
