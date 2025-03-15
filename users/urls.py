from django.urls import path
from .views import SendOTPView, UserDetailView, UserListView, VerifyOTPView, RegisterView, LoginUserView, UpdateUserView, ffLoginView, finalLoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('', UserListView.as_view(), name='user_list'),  # عرض جميع المستخدمين
    path('send_otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('register/', RegisterView.as_view(), name='register'),
    #path('login/', LoginUserView.as_view(), name='login'),
    path('update/<int:user_id>/', UpdateUserView.as_view(), name='update_user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('login/', finalLoginView.as_view(), name='login'),
    path('fflogin/', ffLoginView.as_view(), name='fflogin'),
    path('otheruser/<int:user_id>/', UserDetailView.as_view(), name='otheruser'),
    
]
