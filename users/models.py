from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('customer', 'Customer'),
        ('merchant', 'Merchant'),
    ]

   
    username = models.CharField(max_length=150, unique=True, null=False, blank=False)  # اسم المستخدم يجب أن يكون فريدًا
    phone = models.CharField(max_length=9, unique=True, null=False, blank=False)  # رقم الهاتف فريد أيضًا
    name = models.CharField(max_length=100, null=False, blank=False)  # الاسم العادي لا يحتاج أن يكون فريدًا

    password = models.CharField(max_length=255)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, null=False, blank=False)

    verification_code = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # تعيين username كحقل أساسي
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone', 'name', 'user_type']  # الحقول المطلوبة عند إنشاء المستخدم

    def __str__(self):
        return self.username  # عرض اسم المستخدم عند طباعة الكائن
