import random
import secrets
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from users.serializers import LoginSerializer, UserSerializer
from .models import CustomUser  # تحديث الاستيراد

import logging

User = get_user_model()

def send_otp(phone):
    try:
        user = CustomUser.objects.get(phone=phone)  # استخدام CustomUser هنا
        otp = random.randint(100000, 999999)
        user.verification_code = str(otp)
        user.save()
        return True
    except CustomUser.DoesNotExist:  # تغيير User إلى CustomUser
        return False

def verify_otp(phone, otp):
    try:
        user = CustomUser.objects.get(phone=phone)  # استخدام CustomUser هنا
        print(f"User OTP in DB: {user.verification_code}, Entered OTP: {otp}")  # تحقق من القيم

        if user.verification_code and user.verification_code.strip() == otp.strip():
            user.is_verified = True
            user.verification_code = None
            user.save()
            print("OTP verification successful")
            return True
        
        print("OTP mismatch or already null")
        return False

    except CustomUser.DoesNotExist:
        print("User does not exist")
        return False



# إعدادات الـ logger
logger = logging.getLogger(__name__)
def register_user(request):
    # استرجاع البيانات من الطلب
    data = request.data
    password = data.get('password')

    # استخدام الـ serializer للتحقق من صحة البيانات
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            otp = secrets.randbelow(899999) + 100000
            user.verification_code = str(otp)
            user.save()
            return Response({"message": "تم التسجيل بنجاح. الرجاء التحقق من رقم الهاتف."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return Response({"error": "حدث خطأ أثناء حفظ البيانات."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    logger.error(f"Validation errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        return Response({
            "message": "تم تسجيل الدخول بنجاح.",
            "user_id": user.id,
            "username": user.username,
            "name": user.name,
            "phone": user.phone,
            "user_type": user.user_type,
            "is_verified": user.is_verified,
        }, status=status.HTTP_200_OK)

        return Response({"message": "تم تسجيل الدخول بنجاح.", "user_id": user.id, "user_type": user.user_type}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


