from django.urls import path
from .views import ServiceByCategoryAPIView, ServiceCatalogAPIView, ServiceCreateAPIView, ServiceDetailAPIView, ServiceListAPIView, ServiceSearchAPIView, ServiceUpdateAPIView, ServiceDeleteAPIView

urlpatterns = [
    path('services/create/', ServiceCreateAPIView.as_view(), name='service_create'),
    path('services/<int:pk>/update/', ServiceUpdateAPIView.as_view(), name='service_update'),
    path('services/<int:pk>/delete/', ServiceDeleteAPIView.as_view(), name='service_delete'),
    path('services/', ServiceListAPIView.as_view(), name='service-list'),
    path('services/<int:id>/', ServiceDetailAPIView.as_view(), name='service-detail'),
    path('services/category/<int:category_id>/', ServiceByCategoryAPIView.as_view(), name='service-by-category'),
    path('filter/', ServiceCatalogAPIView.as_view(), name='service-filter'),
    path('search/', ServiceSearchAPIView.as_view(), name='service_search')

]
