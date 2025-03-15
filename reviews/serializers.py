from rest_framework import serializers

from stores.models import Store
from .models import Review
from django.contrib.auth import get_user_model

User = get_user_model()  # جلب نموذج المستخدم المخصص

class EvaluationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)  # اسم العميل
    

    class Meta:
        model = Review
        fields = ['id', 'customer_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'customer_name', 'created_at'] # إضافة المتجر الذي يتم التقييم له


    def validate(self, data):
        # التأكد من عدم وجود تقييم سابق لنفس العميل والمتجر
        customer = data.get('customer')
        store = data.get('store')
        if Review.objects.filter(customer=customer, store=store).exists():
            raise serializers.ValidationError("You have already reviewed this store.")
        return data


    def validate_rating(self, value):
        """
        التحقق من أن التقييم بين 1 و 5
        """
        if not (1 <= value <= 5):
            raise serializers.ValidationError("التقييم يجب أن يكون بين 1 و 5.")
        return value

    def validate_comment(self, value):
        """
        التحقق من أن التعليق غير فارغ.
        """
        if not value.strip():  # .strip() هي دالة تقوم بإزالة المسافات البيضاء من بداية ونهاية النص
            raise serializers.ValidationError("التعليق لا يمكن أن يكون فارغًا.")
        return value

    def create(self, validated_data):
        """
        إنشاء التقييم مع ربط العميل بالمتجر.
        """
        # هنا يتم استخدام البيانات المعتمدة وربط العميل (customer) تلقائيًا
        return super().create(validated_data)
    






class eeEvaluationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)  # اسم العميل
    rating = serializers.IntegerField()
    comment = serializers.CharField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    

    class Meta:
        model = Review
        fields = ['id', 'customer_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'customer_name', 'created_at'] # إضافة المتجر الذي يتم التقييم له


    def validate(self, data):
        # التأكد من عدم وجود تقييم سابق لنفس العميل والمتجر
        customer = data.get('customer')
        store = data.get('store')
        if Review.objects.filter(customer=customer, store=store).exists():
            raise serializers.ValidationError("You have already reviewed this store.")
        return data


    def validate_rating(self, value):
        """
        التحقق من أن التقييم بين 1 و 5
        """
        if not (1 <= value <= 5):
            raise serializers.ValidationError("التقييم يجب أن يكون بين 1 و 5.")
        return value

    def validate_comment(self, value):
        """
        التحقق من أن التعليق غير فارغ.
        """
        if not value.strip():  # .strip() هي دالة تقوم بإزالة المسافات البيضاء من بداية ونهاية النص
            raise serializers.ValidationError("التعليق لا يمكن أن يكون فارغًا.")
        return value

    def create(self, validated_data):
        """
        إنشاء التقييم مع ربط العميل بالمتجر.
        """
        # هنا يتم استخدام البيانات المعتمدة وربط العميل (customer) تلقائيًا
        return super().create(validated_data)
