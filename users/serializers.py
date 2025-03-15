
from venv import logger
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser
from django.contrib.auth import authenticate



User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    permission_classes = [AllowAny]
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'phone', 'name', 'password', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True},  # كلمة المرور تُكتب فقط ولا تُعرض
        }

    def create(self, validated_data):
        # إنشاء المستخدم مع تعيين كلمة المرور بشكل مشفر
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            phone=validated_data['phone'],
            name=validated_data['name'],
            user_type=validated_data['user_type'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        # إذا كانت كلمة المرور موجودة في البيانات المدخلة، نقوم بتشفيرها قبل حفظها.
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])  # تشفير كلمة المرور
        return super().update(instance, validated_data)

    


class LoginSerializer(serializers.Serializer):
    permission_classes = [AllowAny]
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get('phone')
        password = data.get('password')
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid credentials.")
        
        if not user.is_verified:
            raise serializers.ValidationError("Phone number is not verified.")
        
        data['user'] = user
        return data
    


class finalLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)  # إضافة رقم الهاتف
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        phone = attrs.get('phone')

        # التحقق من بيانات المستخدم
        logger.debug(f"Trying to authenticate user: {username} with phone: {phone}")
        
        # نبحث عن المستخدم باستخدام اسم المستخدم ورقم الهاتف
        try:
            user = CustomUser.objects.get(username=username, phone=phone)
        except CustomUser.DoesNotExist:
            logger.warning(f"Authentication failed for user: {username} with phone: {phone}")
            raise serializers.ValidationError({'error': 'اسم المستخدم أو رقم الهاتف غير صحيح.'})

        if not user.is_verified:
            logger.warning(f"User {username} is not verified.")
            raise serializers.ValidationError({'error': 'الحساب غير مفعل. يرجى التحقق من البريد الإلكتروني أو رقم الهاتف.'})

        # إنشاء رموز JWT
        refresh = RefreshToken.for_user(user)
        attrs['access'] = str(refresh.access_token)
        attrs['refresh'] = str(refresh)
        attrs['user_type'] = user.user_type
        attrs['phone'] = user.phone
        attrs['name'] = user.name

        # إضافة المستخدم للتحقق لاحقًا في الـ View
        attrs['user'] = user

        logger.debug(f"Authentication succeeded for user: {username}")
        return attrs