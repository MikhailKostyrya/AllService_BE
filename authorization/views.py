from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from AllService_BE import settings
from .models import User
from authorization.serializers import ResetPasswordSerializer, SendVerificationCodeSerializer, UserLoginSerializer, UserSerializer,UserRegistrationSerializer, VerifyVerificationCodeSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
import cachetools
from django.urls import reverse
import random
import string

cache = cachetools.TTLCache(maxsize=100, ttl=600)

class VerifyAccountView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id, is_active=False)
            user.is_active = True
            user.save()
            return Response({"message": "Account activated successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Invalid or expired link"}, status=status.HTTP_404_NOT_FOUND)

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

        self.send_activation_email(user, request)

        return Response({
            "user": user_data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "User Registered. Activation email sent. Please activate your account."
        }, status=status.HTTP_201_CREATED)

    def send_activation_email(self, user, request):
        activation_link = request.build_absolute_uri(reverse('verify-activation', args=[user.id]))
        context = {
            'user': user,
            'activation_link': activation_link
        }
        html_content = render_to_string("activation_email.html", context)
        text_content = strip_tags(html_content)

        email_message = EmailMultiAlternatives(
            'Activate Your Account',
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

class SendVerificationCodeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SendVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        code = ''.join(random.choice(string.digits) for _ in range(4))
        cache[user.email] = code

        context = {'code': code, 'user': user}
        html_content = render_to_string('verification_email.html', context)
        text_content = strip_tags(html_content)

        email_message = EmailMultiAlternatives(
            'Your Activation Code',
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        return Response({"message": "Verification code sent to email"}, status=status.HTTP_200_OK)

class VerifyVerificationCodeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VerifyVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        user = User.objects.get(email=email)

        if email not in cache:
            return Response({"error": "Verification code has expired."}, status=status.HTTP_400_BAD_REQUEST)
        if cache[email] != code:
            return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)

        del cache[email]
        return Response({"message": "Verification code is valid."}, status=status.HTTP_200_OK)

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
