from catalog.models import Category, Service
from rest_framework import serializers
from users.models import ExecutorData
from django.contrib.auth import get_user_model


User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id']

class ExecutorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutorData
        fields = ['id']


class ServiceSerializer(serializers.ModelSerializer):
    executor = ExecutorDataSerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Service
        fields = ['id', 'name', 'content', 'timetable', 'adress', 'price', 'executor', 'category']

    def create(self, validated_data):
        request = self.context.get('request')
        category = validated_data.pop('category')
        executor = ExecutorData.objects.get(user=request.user)
        service = Service.objects.create(executor=executor, category=category, **validated_data)
        return service
