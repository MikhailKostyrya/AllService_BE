from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from users.models import User
from catalog.models import Service
from catalog.serializers import ServiceSerializer
from request.models import Request, Status

# Created by Evgeniy Sakov

class RecommendationView(APIView):

    @staticmethod
    def jaccard_index(set1, set2):
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union != 0 else 0

    @staticmethod
    def get_user_service_ids(user):
        return set(Request.objects.filter(user=user, status=Status.COMPLETED).values_list('service_id', flat=True))

    @staticmethod
    def get_user_category_ids(service_ids):
        return set(Service.objects.filter(id__in=service_ids).values_list('category_id', flat=True))

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        if not user.is_authenticated:
            return Response({'error': 'User is not authenticated'}, status=401)
        
        user_city_id = user.city_id

        user_service_ids = self.get_user_service_ids(user)

        if not user_service_ids:
            return Response({'recommended_services': []})

        user_category_ids = self.get_user_category_ids(user_service_ids)
        similarity_scores = {}

        other_users = User.objects.exclude(id=user_id).filter(city_id=user_city_id)

        for other_user in other_users:
            other_user_service_ids = self.get_user_service_ids(other_user)
            other_user_category_ids = self.get_user_category_ids(other_user_service_ids)
            similarity_scores[other_user.id] = self.jaccard_index(user_category_ids, other_user_category_ids)

        recommended_services = set()
        sorted_users = sorted(similarity_scores, key=similarity_scores.get, reverse=True)

        for similar_user_id in sorted_users:
            similar_user = get_object_or_404(User, id=similar_user_id)
            similar_user_service_ids = self.get_user_service_ids(similar_user)
            similar_user_category_ids = self.get_user_category_ids(similar_user_service_ids)

            new_recommendations = Service.objects.filter(
                category_id__in=similar_user_category_ids,
                city_id=user_city_id
            ).exclude(id__in=user_service_ids)

            recommended_services.update(new_recommendations.values_list('id', flat=True))

        recommended_services_qs = Service.objects.filter(id__in=recommended_services)
        serializer = ServiceSerializer(recommended_services_qs, many=True)

        return Response({'recommended_services': serializer.data})
