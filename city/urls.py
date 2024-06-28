from django.urls import path
from .views import CityDetailView, CityView, UserCitySelectionView

urlpatterns = [
    path('', CityView.as_view(), name='get-city'),
    path('<int:city_id>/', CityDetailView.as_view(), name='city-detail'),
    path('select/', UserCitySelectionView.as_view(), name='user_city_select'),
]
