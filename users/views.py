import secrets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, LoginSerializer
from .services import send_otp, verify_otp, register_user, login_user
from .models import CustomUser
import logging
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate


# إعدادات السجل لتسجيل الأخطاء
logger = logging.getLogger(__name__)


class UserDetailView(APIView):
    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class UserListView(APIView):
    def get(self, request):
        try:
            users = CustomUser.objects.all()  # استخدام CustomUser بدلاً من User
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in UserListView: {e}")
            return Response({"error": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendOTPView(APIView):
    def post(self, request):
        try:
            phone = request.data.get("phone")
            result = send_otp(phone)
            if result:
                return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in SendOTPView: {e}")
            return Response({"error": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(APIView):
    def post(self, request):
        try:
            phone = request.data.get("phone")
            otp = request.data.get("otp")
            result = verify_otp(phone, otp)
            if result:
                return Response({"message": "تم التحقق بنجاح."}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in VerifyOTPView: {e}")
            return Response({"error": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""
class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "تم التسجيل بنجاح."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # إنشاء التوكن هنا مباشرةً بعد إنشاء المستخدم
            refresh = TokenObtainPairSerializer.get_token(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # تضمين الـ id في الاستجابة
            return Response({
                'id': user.id,  # إضافة معرف المستخدم
                'access': access_token,
                'refresh': refresh_token,
                'user': serializer.data  # يمكنك تضمين بيانات المستخدم الأخرى أيضًا
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ffLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # الحصول على البيانات
        login_field = request.data.get("login_field")  # الحقل الأول قد يكون اسم المستخدم أو رقم الهاتف
        password = request.data.get("password")  # كلمة المرور

        logger.debug(f"Received login request with login_field: {login_field}")

        # التحقق من أن كلمة المرور ليست فارغة
        if not password:
            logger.error("Password is required.")
            return Response({'error': 'كلمة المرور مطلوبة'}, status=status.HTTP_400_BAD_REQUEST)

        # البحث في قاعدة البيانات باستخدام اسم المستخدم أو رقم الهاتف
        try:
            if '@' in login_field:  # إذا كان يحتوي على @ فهو على الأرجح بريد إلكتروني
                user = CustomUser.objects.get(email=login_field)
            elif len(login_field) == 9 and login_field.isdigit():  # إذا كان يحتوي على 9 أرقام فهو رقم الهاتف
                user = CustomUser.objects.get(phone=login_field)
            else:  # إذا كان نصًا عاديًا فهو اسم المستخدم
                user = CustomUser.objects.get(username=login_field)
        except CustomUser.DoesNotExist:
            logger.error(f"Authentication failed for login_field: {login_field}")
            return Response({'error': 'البيانات المدخلة غير صحيحة'}, status=status.HTTP_400_BAD_REQUEST)

        # التحقق من صحة كلمة المرور
        user = authenticate(username=user.username, password=password)

        if user:
            logger.info(f"User {user.username} authenticated successfully.")
            refresh = TokenObtainPairSerializer.get_token(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # تضمين بيانات المستخدم في الاستجابة
            user_data = {
                'id': user.id,
                'access': access_token,
                'refresh': refresh_token,
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'name': user.name,
                    'user_type': user.user_type,
                }
            }
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            logger.error(f"Invalid password for user {user.username}")
            return Response({'error': 'كلمة المرور غير صحيحة'}, status=status.HTTP_400_BAD_REQUEST)
        

        
        
class finalLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = finalLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')

            # البيانات التي سيتم إرجاعها
            response_data = {
                'username': user.username,
                'user_type': user.user_type,
                'id': user.id,  # إضافة ID المستخدم
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        # إرجاع الأخطاء
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class LoginUserView(APIView):
    def post(self, request):
        try:
            return login_user(request)
        except Exception as e:
            logger.error(f"Error in LoginUserView: {e}")
            return Response({"error": "LoginSomething went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateUserView(APIView):
    def put(self, request, user_id):
        try:
            user = get_object_or_404(CustomUser, id=user_id)
            serializer = UserSerializer(user, data=request.data, partial=True)  # استخدام PATCH للتعديل الجزئي
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "تم التحديث بنجاح.", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in UpdateUserView: {e}")
            return Response({"error": "UpdateSomething went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
