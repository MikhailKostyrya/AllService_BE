from rest_framework import serializers
from .models import Request


class RequestCreateSerializer(serializers.ModelSerializer):
    date_times = serializers.ListField(
        child=serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S"),
        allow_empty=True
    )
    
    class Meta:
        model = Request
        fields = ['address', 'create_date', 'date_times', 'user', 'service']


class RequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'status', 'address', 'create_date', 'date_times', 'user', 'service']


class RequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['status', 'address', 'create_date', 'date_times', 'user', 'service']


class RequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['status']
