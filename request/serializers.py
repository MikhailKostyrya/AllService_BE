from rest_framework import serializers
from .models import Request


class RequestCreateSerializer(serializers.ModelSerializer):
    date_times = serializers.ListField(
        child=serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S"),
        allow_empty=True
    )
    
    class Meta:
        model = Request
        fields = ['create_date', 'date_times', 'service']



class RequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'status', 'address', 'create_date', 'date_times', 'user', 'service', "price"]


class RequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'status', 'create_date', 'date_times', 'service', "price"]


class RequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['status']
