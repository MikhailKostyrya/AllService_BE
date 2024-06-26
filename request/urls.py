from django.urls import path
from .views import ExecutorRequestsListView, RequestDetailAPIView, RequestCreateAPIView, AllRequestListAPIView, RequestStatusUpdateAPIView

urlpatterns = [
    path('create/', RequestCreateAPIView.as_view(), name='request_create'),
    path('<int:id>/', RequestDetailAPIView.as_view(), name='request-detail'),
    path('user-requests/', AllRequestListAPIView.as_view(), name='request-list-user'),
    path('<int:id>/status-update/', RequestStatusUpdateAPIView.as_view(), name='request-status-update'),
    path('executor/<int:service_id>/', ExecutorRequestsListView.as_view(), name='executor-requests-list'),

]
