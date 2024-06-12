from authorization.models import ExecutorData, User
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

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

class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'second_name')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user
    

class SendActivationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyActivationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(max_length=128)
