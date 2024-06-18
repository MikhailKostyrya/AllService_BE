from django.shortcuts import render
from rest_framework.response import Response
from users.models import ExecutorData
from .models import Service
from .serializers import ServiceSerializer
from rest_framework import generics, status, mixins
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


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


class ServiceListAPIView(generics.ListAPIView):
    """
    get:
    Return a list of all services.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    @swagger_auto_schema(operation_description="Get all services")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ServiceDetailAPIView(generics.RetrieveAPIView):
    """
    get:
    Return the details of a specific service by ID.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    lookup_field = 'id'

    @swagger_auto_schema(operation_description="Get details of a specific service by ID")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ServiceByCategoryAPIView(generics.ListAPIView):
    """
    get:
    Return a list of services filtered by category ID.
    """
    serializer_class = ServiceSerializer

    @swagger_auto_schema(operation_description="Get all services filtered by category ID")
    def get(self, request, *args, **kwargs):
        category_id = self.kwargs['category_id']
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Service.objects.filter(category_id=category_id)


class ServiceCatalogAPIView(generics.GenericAPIView):
    serializer_class = ServiceSerializer


    def get(self, request, category_name=None):
        order_by = request.GET.get('order_by', None)
        min_price = request.GET.get('min_price', None)
        max_price = request.GET.get('max_price', None)
        query = request.GET.get('q', None)

        services = Service.objects.all()

        def q_search(query):
            vector = SearchVector("name", "content")
            query = SearchQuery(query)
            return Service.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gt=0).order_by("-rank")


        if category_name and category_name != 'all':
            services = Service.objects.filter(category__category_name=category_name)
            
        if query:
            services = q_search(query)

        if min_price is not None:
            services = services.filter(price__gte=min_price)
        if max_price is not None:
            services = services.filter(price__lte=max_price)

        if order_by and order_by != 'default':
            services = services.order_by(order_by)

        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
