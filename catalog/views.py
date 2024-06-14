from django.shortcuts import render
from rest_framework.response import Response

from users.models import ExecutorData
from .models import Service
from catalog.serializers import ServiceSerializer
from rest_framework import generics, status, mixins


class ServiceCreateAPIView(generics.GenericAPIView):
    serializer_class = ServiceSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = serializer.save()

        return Response({
            "service": ServiceSerializer(service, context={'request': request}).data,
            "message": "Service created successfully"
        }, status=status.HTTP_201_CREATED)


class ServiceUpdateAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        executor = request.user.executor_data
        service = serializer.save(executor=executor)

        return Response({
            "service": ServiceSerializer(service, context={'request': request}).data,
            "message": "Service updated successfully"
        }, status=status.HTTP_200_OK)


class ServiceDeleteAPIView(generics.DestroyAPIView):
    queryset = Service.objects.all()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Service deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()