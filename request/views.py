from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from .date_utils import filter_out_busy_times, get_date_times_from_json
from catalog.models import Service
from catalog.serializers import User
from .models import Request
from .serializers import RequestCreateSerializer, RequestDetailSerializer, RequestListSerializer, RequestStatusSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from datetime import datetime, timedelta


class RequestCreateAPIView(generics.GenericAPIView):
    serializer_class = RequestCreateSerializer

    @swagger_auto_schema(request_body=RequestCreateSerializer)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        service = serializer.validated_data['service']
        price = service.price
        address = service.address
        if not address:
            address = request.data.get('address')
        serializer.save(price=price, address=address, user=user)

        return Response({
            "request": RequestCreateSerializer(serializer.instance, context={'request': request}).data,
            "message": "Request created successfully"
        }, status=status.HTTP_201_CREATED)




class RequestDetailAPIView(generics.RetrieveAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestDetailSerializer
    lookup_field = 'id'

    @swagger_auto_schema(operation_description="Get details of a specific request by ID")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AllRequestListAPIView(generics.ListAPIView):
    serializer_class = RequestListSerializer

    def get_queryset(self):
        user = self.request.user
        return Request.objects.filter(user=user)
 

class RequestStatusUpdateAPIView(APIView):

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
    

class AvailableTimesAPIView(APIView):

    def get(self, request, *args, **kwargs):
        service_id = self.kwargs.get('service_id')
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))

        service = get_object_or_404(Service, id=service_id)
        schedule_json = service.timetable

        date_times = get_date_times_from_json(schedule_json, year, month)

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        busy_requests = Request.objects.filter(
            service=service,
            date_times__0__gte=start_date,
            date_times__0__lt=end_date
        )

        busy_times = []
        for request in busy_requests:
            for time_range in request.date_times:
                busy_start = time_range.replace(tzinfo=None)  # Приведение к offset-naive
                busy_end = busy_start + timedelta(hours=1)  # Предположим, что длительность записи - 1 час
                busy_times.append((busy_start, busy_end))

        available_times = filter_out_busy_times(date_times, busy_times)

        return Response({
            "available_times": available_times,
        }, status=status.HTTP_200_OK)
