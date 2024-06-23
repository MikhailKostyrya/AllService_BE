from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from catalog.models import Service
from catalog.serializers import User
from .models import Request
from .serializers import RequestCreateSerializer, RequestDetailSerializer, RequestListSerializer, RequestStatusSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView


class RequestCreateAPIView(generics.GenericAPIView):
    serializer_class = RequestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=RequestCreateSerializer)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        request_instance = serializer.save()

        return Response({
            "request": RequestCreateSerializer(request_instance, context={'request': request}).data,
            "message": "Request created successfully"
        }, status=status.HTTP_201_CREATED)


class RequestDetailAPIView(generics.RetrieveAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestDetailSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_description="Get details of a specific request by ID")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AllRequestListAPIView(generics.ListAPIView):
    serializer_class = RequestListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Request.objects.filter(user=user)
 

class RequestStatusUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=RequestStatusSerializer)
    def put(self, request, id):
        request_instance = Request.objects.get(id=id)
        user = request.user
        if not user.is_executor:
            return Response({"error": "You do not have permission to update this request as you are not an executor"}, status=status.HTTP_403_FORBIDDEN)

        if request_instance.user == request.user:
            return Response({"error": "You do not have permission to update this request"}, status=status.HTTP_403_FORBIDDEN)

        serializer = RequestStatusSerializer(request_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "request": RequestStatusSerializer(request_instance, context={'request': request}).data,
            "message": "Request status updated successfully"
        }, status=status.HTTP_200_OK)


class ExecutorRequestsListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RequestListSerializer

    def get_queryset(self):
        user = get_object_or_404(User, email=self.request.user.email)
        if not user.is_executor:
            return Request.objects.none()
        
        service_id = self.kwargs.get('service_id')
        if service_id:
            service = get_object_or_404(Service, id=service_id)
            return Request.objects.filter(service=service, service__executor__user=user)
        return Request.objects.filter(service__executor__user=user)