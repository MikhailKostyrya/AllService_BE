from django.shortcuts import render
from elasticsearch import ElasticsearchException
from rest_framework.response import Response
from .pagination import CustomPagination
from search.client import ElasticClient
from django.forms import model_to_dict
from users.models import ExecutorData
from .models import Category, Service
from .serializers import CategorySerializer, ServiceSearchSerializer, ServiceSerializer
from rest_framework import generics, status, mixins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ServiceCreateAPIView(generics.GenericAPIView):
    serializer_class = ServiceSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Service name'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Service content'),
                'timetable': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Timetable example: {'Monday': ['09:00-11:00', '14:00-16:00'], 'Tuesday': ['10:00-12:00']}",
                    additional_properties=openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING))
                ),
                'city': openapi.Schema(type=openapi.TYPE_INTEGER, description='City ID'),
                'address': openapi.Schema(type=openapi.TYPE_STRING, description='Address'),
                'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Price'),
                'executor': openapi.Schema(type=openapi.TYPE_INTEGER, description='Executor ID'),
                'category': openapi.Schema(type=openapi.TYPE_INTEGER, description='Category ID'),
                'photo': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY, description='Photo'),
            },
            required=['name', 'content', 'timetable', 'price', 'executor', 'category']
        ),
        responses={201: ServiceSerializer}
    )
    def post(self, request):
        """Создание услуги"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = serializer.save()
        self.update_elastic(service)

        return Response({
            "service": ServiceSerializer(service, context={'request': request}).data,
            "message": "Service created successfully"
        }, status=status.HTTP_201_CREATED)
    
    def update_elastic(self, service):
        client = ElasticClient()
        try:
            data = [{"index": {"_index": client.index, "_id": service.id}}]
            service_dict = model_to_dict(service, fields=[field.name for field in service._meta.fields])
            data.append(service_dict)
            client.bulk(data)
        except ElasticsearchException as e:
            print(f"An error occurred while indexing the service: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    

class ServiceSearchAPIView(generics.GenericAPIView):
    serializer_class = ServiceSerializer
    pagination_class = None

    @swagger_auto_schema(request_body=ServiceSearchSerializer, responses={200: ServiceSerializer(many=True)})
    def post(self, request):
        """Поиск услуг"""
        search = request.data['search']
        client = ElasticClient()
        service_ids = client.search(search)
        services = Service.objects.filter(id__in=service_ids)
        return Response(ServiceSerializer(services, many=True).data, status=200)


class ServiceUpdateAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Редактирование услуги"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        executor = request.user.executor_data
        service = serializer.save(executor=executor)

        self.update_elastic(service)

        return Response({
            "service": ServiceSerializer(service, context={'request': request}).data,
            "message": "Service updated successfully"
        }, status=status.HTTP_200_OK)

    def update_elastic(self, service):
        client = ElasticClient()
        data = [{"index": {"_index": client.index, "_id": service.id}}]
        service_dict = model_to_dict(service, fields=[field.name for field in service._meta.fields])
        data.append(service_dict)
        client.bulk(data)


class ServiceDeleteAPIView(generics.DestroyAPIView):
    queryset = Service.objects.all()

    def delete(self, request, *args, **kwargs):
        """Удаление услуги"""
        instance = self.get_object()
        self.perform_destroy(instance)
        self.delete_from_elastic(instance)

        return Response({
            "message": "Service deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()

    def delete_from_elastic(self, service):
        client = ElasticClient()
        client.delete_document(service.id)


class ServiceListAPIView(generics.ListAPIView):
    """
    get:
    Return a list of all services.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    pagination_class = CustomPagination

    @swagger_auto_schema(operation_description="Get all services")
    def get(self, request, *args, **kwargs):
        user = request.user
        city_name = user.city.name if user.is_authenticated else None

        services = self.queryset
        if city_name:
            services = services.filter(city__name=city_name)
            
        page = self.paginate_queryset(services)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    pagination_class = CustomPagination

    @swagger_auto_schema(operation_description="Get all services filtered by category ID")
    def get(self, request, *args, **kwargs):
        category_id = self.kwargs['category_id']
        user = request.user
        city_id = user.city_id if user.is_authenticated else None

        services = Service.objects.filter(category_id=category_id)
        if city_id is not None:
            services = services.filter(city_id=city_id)
            
        page = self.paginate_queryset(services)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceCatalogAPIView(generics.GenericAPIView):
    serializer_class = ServiceSerializer
    pagination_class = CustomPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('order_by', openapi.IN_QUERY, description="Order by field (price_asc, price_desc, date_asc, date_desc)", type=openapi.TYPE_STRING),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('category_id', openapi.IN_QUERY, description="Category ID", type=openapi.TYPE_INTEGER),

        ]
    )
    def get(self, request, category_name=None):
        order_by = request.GET.get('order_by', None)
        min_price = request.GET.get('min_price', None)
        max_price = request.GET.get('max_price', None)
        category_id = request.GET.get('category_id', None)

        user = request.user
        if user.is_authenticated:
            city_id = user.city_id
        else:
            city_id = None

        services = Service.objects.all()

        if category_name and category_name != 'all':
            services = services.filter(category__category_name=category_name)

        if min_price is not None:
            services = services.filter(price__gte=min_price)
        if max_price is not None:
            services = services.filter(price__lte=max_price)

        if city_id is not None:
            services = services.filter(city_id=city_id)

        if order_by:
            if order_by == 'price_asc':
                services = services.order_by('price')
            elif order_by == 'price_desc':
                services = services.order_by('-price')
            elif order_by == 'date_asc':
                services = services.order_by('created_at')
            elif order_by == 'date_desc':
                services = services.order_by('-created_at')

        page = self.paginate_queryset(services)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None
    
    @swagger_auto_schema(operation_description="Get all categories")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
