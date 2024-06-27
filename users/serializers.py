from users.models import ExecutorData, User
from rest_framework import serializers


class ExecutorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutorData
        fields = ['id', 'content', 'contact_executor', 'inn']
        ref_name = 'UsersExecutorData'


class UserSerializer(serializers.ModelSerializer):
    executor_data = ExecutorDataSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'second_name', 'email', 'contact', 'is_executor', 'executor_data', 'photo']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def update(self, instance, validated_data):
        executor_data = validated_data.pop('executor_data', None)
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if instance.is_executor and executor_data is not None:
            ExecutorData.objects.update_or_create(defaults=executor_data, user=instance)
        
        return instance

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
        user = User.objects.create_user(is_active=False, **validated_data)
        return user
    

class SendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)
    new_password = serializers.CharField(max_length=128)
