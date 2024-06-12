from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from AllService_BE import settings
from .models import User
from authorization.serializers import ResetPasswordSerializer, SendActivationCodeSerializer, UserLoginSerializer, UserSerializer,UserRegistrationSerializer, VerifyActivationCodeSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
import cachetools
import random
import string
import logging as logger


cache = cachetools.TTLCache(maxsize=100, ttl=600)


class UserLoginAPIView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user, context={'request': request}).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "User Logged In Successfully."
            }, status=status.HTTP_200_OK)
        return Response({"message": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserRegistrationAPIView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user, context={'request': request}).data

        return Response({
            "user": user_data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "User Registered and Logged In Successfully."
        }, status=status.HTTP_201_CREATED)



class SendActivationCodeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SendActivationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        code = ''.join(random.choice(string.digits) for _ in range(4))
        cache[user.email] = code

        context = {'code': code, 'user': user}
        html_content = render_to_string('activation_email.html', context)
        text_content = strip_tags(html_content)

        email_message = EmailMultiAlternatives(
            'Your Activation Code',
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        return Response({"message": "Activation code sent to email"}, status=status.HTTP_200_OK)

class VerifyActivationCodeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VerifyActivationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        user = User.objects.get(email=email)

        if email not in cache:
            return Response({"error": "Activation code has expired."}, status=status.HTTP_400_BAD_REQUEST)
        if cache[email] != code:
            return Response({"error": "Invalid activation code."}, status=status.HTTP_400_BAD_REQUEST)

        del cache[email]
        return Response({"message": "Activation code is valid."}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        if email in cache:
            del cache[email]

        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)