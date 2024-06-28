from rest_framework import views
from rest_framework.response import Response
from .models import City
from .serializers import CitySerializer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from users.models import  User
from rest_framework.permissions import IsAuthenticated


class CityView(views.APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('format', openapi.IN_QUERY, description="Response format", type=openapi.TYPE_STRING)
        ],
        responses={200: CitySerializer(many=True)}
    )
    def get(self, request, format=None):
        city = City.objects.all()
        serializer = CitySerializer(city, many=True)
        return Response(serializer.data)

class CityDetailView(views.APIView):
    @swagger_auto_schema(responses={200: CitySerializer})
    def get(self, request, city_id, format=None):
        try:
            city = City.objects.get(id=city_id)
            serializer = CitySerializer(city)
            return Response({'name': serializer.data['name']})
        except City.DoesNotExist:
            return Response({'error': 'City not found'}, status=status.HTTP_404_NOT_FOUND)



class UserCitySelectionView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('city_id', openapi.IN_QUERY, description="City ID", type=openapi.TYPE_INTEGER)
        ],
        responses={200: openapi.Response('City selected successfully', CitySerializer)}
    )
    def post(self, request, format=None):
        city_id = request.query_params.get('city_id')
        if not city_id:
            return Response({'error': 'City ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            city = City.objects.get(id=city_id)
            user = request.user
            user.city = city
            user.save()
            serializer = CitySerializer(city)
            return Response({'message': 'City selected successfully', 'data': serializer.data})
        except City.DoesNotExist:
            return Response({'error': 'City not found'}, status=status.HTTP_404_NOT_FOUND)