from catalog.models import Category, Service
from rest_framework import serializers
from users.models import ExecutorData
from city.models import City
from django.contrib.auth import get_user_model


User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'photo']


class ExecutorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutorData
        fields = ['id']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name']
        ref_name = 'CitySerializer'


class ServiceSerializer(serializers.ModelSerializer):
    executor = ExecutorDataSerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    timetable = serializers.DictField(child=serializers.ListField(child=serializers.CharField()), required=False, help_text="Example: { 'Monday': ['09:00-11:00', '14:00-16:00'], 'Tuesday': ['10:00-12:00'] }")
    city = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'content', 'timetable', 'city', 'address', 'price', 'executor', 'category']

    def create(self, validated_data):
        request = self.context.get('request')
        category = validated_data.pop('category')
        executor = ExecutorData.objects.get(user=request.user)
        service = Service.objects.create(executor=executor, category=category, **validated_data)
        return service


class ServiceSearchSerializer(serializers.Serializer):
    search = serializers.CharField(max_length=50)