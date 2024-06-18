from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import DeleteAccountView, ResetPasswordView, SendVerificationCodeView, UserLoginAPIView, UserProfileUpdateView, UserRegistrationAPIView, VerifyAccountView, VerifyVerificationCodeView


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('delete/', DeleteAccountView.as_view(), name='delete-account'),
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('send-activation/', SendVerificationCodeView.as_view(), name='send-activation-code'),
    path('verify/', VerifyVerificationCodeView.as_view(), name='verify-activation-code'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('verify-activation/<int:user_id>/', VerifyAccountView.as_view(), name='verify-activation'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),


]
