from rest_framework import serializers
from .models import Request


class RequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['address', 'create_date', 'time', 'user', 'service']


class RequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'status', 'address', 'create_date', 'time', 'user', 'service']


class RequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['status', 'address', 'create_date', 'time', 'user', 'service']


class RequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['status']