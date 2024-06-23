from django.shortcuts import render
from elasticsearch import ElasticsearchException
from rest_framework.response import Response
from serach.client import ElasticClient
from django.forms import model_to_dict
from users.models import ExecutorData
from .models import Service
from .serializers import ServiceSearchSerializer, ServiceSerializer
from rest_framework import generics, status, mixins
from drf_yasg.utils import swagger_auto_schema


class ServiceCreateAPIView(generics.GenericAPIView):
    serializer_class = ServiceSerializer

    def post(self, request):
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
        instance = self.get_object()
        self.perform_destroy(instance)
        self.delete_from_elastic(instance)

        return Response({
            "message": "Service deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

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

        if category_name and category_name != 'all':
            services = Service.objects.filter(category__category_name=category_name)

        if min_price is not None:
            services = services.filter(price__gte=min_price)
        if max_price is not None:
            services = services.filter(price__lte=max_price)

        if order_by and order_by != 'default':
            services = services.order_by(order_by)

        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
