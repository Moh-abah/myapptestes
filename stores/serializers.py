from rest_framework import serializers
from django.contrib.auth import get_user_model
from reviews.serializers import EvaluationSerializer
from users.serializers import UserSerializer
from .models import Store
from django.db.models import Avg

User = get_user_model()
class CStoreSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Store
        fields = ['id', 'owner', 'name_store', 'category', 'subcategory', 'description', 'location', 'images', 'created_at', 'updated_at']
        extra_kwargs = {
            'owner': {'read_only': True},  # owner سيكون معرف من خلال المستخدم المتصل
        }

    def create(self, validated_data):
        # تعيين المالك بشكل تلقائي إلى المستخدم المتصل
        validated_data['owner'] = self.context['request'].user
        store = Store.objects.create(**validated_data)
        return store
    
    
class StoreSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)  # عرض معلومات التاجر (المالك)
    evaluations = EvaluationSerializer(many=True, read_only=True)  # عرض التقييمات المرتبطة بالمتجر
    rating_average = serializers.SerializerMethodField()  # إضافة التقييم المتوسط
    rating_count = serializers.SerializerMethodField() 
    owner_name = serializers.CharField(source="owner.name", read_only=True)  # اسم المالك
    phone = serializers.CharField(source="owner.phone", read_only=True)  # رقم الهاتف من نموذج المستخدم # إضافة عدد التقييمات
    owner_id = serializers.CharField(source="owner.id", read_only=True)
    class Meta:
        model = Store
        fields = [
            'id',
            'name_store',  
            'category',
            'subcategory',
            'description',
            'location',
            'images',
            'owner',
            'owner_name',
            'phone',  
            'evaluations',
            'rating_average',
            'rating_count',
            'owner_id',
             
        ]
        
    def get_location(self, obj):
        # توفير بيانات افتراضية إذا كان location غير صالح
        location_data = obj.location or {}
        return {
            "latitude": location_data.get("latitude", 0.0),
            "longitude": location_data.get("longitude", 0.0),
        }
    def get_rating_average(self, obj):
        # حساب التقييم المتوسط
        return obj.reviews.aggregate(Avg('rating'))['rating__avg'] or 0  # تأكد من توافق علاقة التقييمات

    def get_rating_count(self, obj):
        # حساب عدد التقييمات
        return obj.reviews.count()

    def validate_name_store(self, value):
        # التحقق من صحة اسم المتجر
        if not value.strip():
            raise serializers.ValidationError("اسم المتجر لا يمكن أن يكون فارغًا.")
        return value

    def validate_category(self, value):
        # التحقق من صحة الفئة
        if not value.strip():
            raise serializers.ValidationError("الفئة لا يمكن أن تكون فارغة.")
        return value
    
    

    def validate_subcategory(self, value):
        """
        التحقق من صحة الفئة الفرعية بناءً على الفئة الرئيسية.
        """
        category = self.initial_data.get('category', None)
        if category:
            valid_subcategories = dict(Store.SUBCATEGORY_CHOICES).get(category, [])
            if value and value not in [sub[0] for sub in valid_subcategories]:
                raise serializers.ValidationError(f"الفئة الفرعية {value} غير صالحة للفئة الرئيسية {category}.")
        return value
    

    def get_ratings(self, obj):
    # جلب التقييمات المرتبطة بالمتجر
        evaluations = obj.reviews.all()  # تأكد من أن العلاقة بين المتجر والتقييمات صحيحة
        return EvaluationSerializer(evaluations, many=True).data

class StoreSearchSerializer(serializers.Serializer):
    query = serializers.CharField()

    def validate_query(self, value):
        # التحقق من صحة استعلام البحث
        if not value.strip():
            raise serializers.ValidationError("استعلام البحث لا يمكن أن يكون فارغًا.")
        return value
