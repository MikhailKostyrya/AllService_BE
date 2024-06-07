from authorization.models import ExecutorData, User
from rest_framework import serializers


class ExecutorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutorData
        fields = ['id', 'content', 'contact_executor', 'inn']


class UserSerializer(serializers.ModelSerializer):
    executor_data = ExecutorDataSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'second_name', 'email', 'contact', 'is_executor', 'executor_data']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    # def create(self, validated_data):
    #     executor_data = validated_data.pop('executor_data', None)
    #     user = User.objects.create_user(validated_edit_data)
    #     if executor_data:
    #         executor_data_instance = ExecutorData.objects.create(executor_data)
    #         user.executor_data = executor_data_instance
    #         user.save()
    #     return user

    # def update(self, instance, validated_data):
    #     executor_data = validated_data.pop('executor_data', None)
    #     instance = super(UserSerializer, self).update(instance, validated_data)
    #     if executor_data:
    #         if hasattr(instance, 'executor_data'):
    #             ExecutorData.objects.filter(id=instance.executordata.id).update(executor_data)
    #         else:
    #             instance.executor_data = ExecutorData.objects.create(executor_data)
    #             instance.save()
    #     return instance
