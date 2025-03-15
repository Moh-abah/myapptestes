from ast import Store
from rest_framework import serializers
from django.contrib.auth import get_user_model

from users.models import CustomUser
from users.serializers import UserSerializer
from .models import Message, finalMessage
from .models import Chat



User = get_user_model()  # جلب نموذج المستخدم المخصص


"""
class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())  # يتم تعيين المرسل تلقائيًا
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender','receiver', 'content', 'created_at']

    def validate_content(self, value):
        
        التحقق من أن محتوى الرسالة ليس فارغًا.
        
        if not value.strip():
            raise serializers.ValidationError("محتوى الرسالة لا يمكن أن يكون فارغًا.")
        return value
    
    def validate_chat(self, value):
        
        التحقق من وجود المحادثة بين المستخدمين.
        
        user = self.context['request'].user
        if value.user1 != user and value.user2 != user:
            raise serializers.ValidationError("لا يمكنك إرسال رسائل إلى هذه المحادثة.")
        return value
    
    
class ChatSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)  # تضمين تفاصيل العميل
    merchant = UserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True) 
    last_message = serializers.SerializerMethodField()  # آخر رسالة
    merchant_name = serializers.SerializerMethodField()  # اسم التاجر

    class Meta:
        model = Chat
        fields = ['id', 'customer', 'merchant', 'merchant_name', 'created_at', 'last_message','messages']
        read_only_fields = ['created_at']

    def get_last_message(self, obj):
        
        جلب آخر رسالة في المحادثة.
        
        last_msg = obj.messages.order_by('-created_at').first()
        return MessageSerializer(last_msg).data if last_msg else None

    def get_merchant_name(self, obj):
        
        جلب اسم التاجر (user2).
        
        return obj.user2.name  # Assuming `name` is a field in the User model
    
    
    def create(self, validated_data):
        
        إنشاء المحادثة بين المستخدمين.
        
        user1 = validated_data['user1']
        user2 = validated_data['user2']

        # التأكد من أن المحادثة بين المستخدمين ليست موجودة بالفعل
        chat = Chat.objects.create(user1=user1, user2=user2)
        return chat


"""
# Serializer لنموذج Chat
class ChatSerializer(serializers.ModelSerializer):
    customer = UserSerializer(source="customer", read_only=True)  # عرض معلومات العميل
    merchant = UserSerializer(source="merchant", read_only=True)  # عرض معلومات التاجر

    class Meta:
        model = Chat
        fields = ['id', 'customer', 'merchant', 'created_at', 'updated_at', 'is_active']

    def create(self, validated_data):
        """
        إنشاء محادثة جديدة بين العميل والتاجر.
        """
        # جلب بيانات العميل والتاجر من سياق الطلب
        customer = self.context['request'].user  # المستخدم الحالي هو العميل
        merchant_id = self.initial_data.get('merchant')  # التاجر يتم تمريره كـ ID
        
        if not merchant_id:
            raise serializers.ValidationError({"merchant": "Merchant ID is required."})

        # التحقق من صحة معرف التاجر
        try:
            merchant = CustomUser.objects.get(id=merchant_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"merchant": "Merchant does not exist."})

        # منع إنشاء محادثة بين نفس المستخدم
        if customer == merchant:
            raise serializers.ValidationError({"detail": "Customer and Merchant cannot be the same user."})

        # التحقق من وجود محادثة سابقة
        existing_chat = Chat.objects.filter(customer=customer, merchant=merchant).first()
        if existing_chat:
            return existing_chat

        # إنشاء محادثة جديدة
        chat = Chat.objects.create(
            customer=customer,
            merchant=merchant,
            is_active=True  # قيمة افتراضية
        )
        return chat


class ChatttrSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField(read_only=True)  # عرض معلومات العميل
    merchant = serializers.SerializerMethodField(read_only=True)  # عرض معلومات التاجر
    merchant_id = serializers.IntegerField(write_only=True, required=True)  # تمرير ID التاجر
    store_id = serializers.IntegerField(write_only=True, required=True)  # تمرير store_id

    class Meta:
        model = Chat
        fields = ['id', 'customer', 'merchant', 'store', 'merchant_id', 'store_id', 'created_at', 'updated_at', 'is_active']

    def get_customer(self, obj):
        """
        إرجاع بيانات العميل.
        """
        return {
            "id": obj.customer.id,
            "username": obj.customer.username,
            "name": obj.customer.name
        }

    def get_merchant(self, obj):
        """
        إرجاع بيانات التاجر.
        """
        return {
            "id": obj.merchant.id,
            "username": obj.merchant.username,
            "name": obj.merchant.name
        }

    def create(self, validated_data):
        """
        إنشاء محادثة جديدة بين العميل والتاجر بناءً على المتجر.
        """
        customer = self.context['request'].user  # المستخدم الحالي هو العميل
        merchant_id = validated_data.pop('merchant_id')  # الحصول على التاجر من البيانات
        store_id = validated_data.pop('store_id')  # الحصول على المتجر من البيانات

        # التحقق من صحة معرف التاجر
        try:
            merchant = CustomUser.objects.get(id=merchant_id, user_type='merchant')
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"merchant": "Merchant does not exist."})

        # التحقق من صحة معرف المتجر
        try:
            store = Store.objects.get(id=store_id, owner=merchant)  # المتجر يجب أن يكون مملوكًا للتاجر
        except Store.DoesNotExist:
            raise serializers.ValidationError({"store": "Store does not exist or does not belong to this merchant."})

        # منع إنشاء محادثة بين نفس المستخدم
        if customer == merchant:
            raise serializers.ValidationError({"detail": "Customer and Merchant cannot be the same user."})

        # التحقق من وجود محادثة سابقة
        existing_chat = Chat.objects.filter(customer=customer, merchant=merchant, store=store).first()
        if existing_chat:
            return existing_chat

        # إنشاء محادثة جديدة
        chat = Chat.objects.create(
            customer=customer,
            merchant=merchant,
            store=store,  # ربط المحادثة بالمتجر
            is_active=True  # قيمة افتراضية
        )
        return chat

# Serializer لنموذج Message
class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())  # تعيين المرسل تلقائيًا
    receiver = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())  # اختيار المستقبل

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'receiver', 'content', 'created_at']
        read_only_fields = ['created_at']  # هذا الحقل للقراءة فقط


class MMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'created_at', 'sender', 'is_read']



class ChatWithMessagesSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)  # تفاصيل العميل
    merchant = UserSerializer(read_only=True)  # تفاصيل التاجر
    messages = serializers.SerializerMethodField()  # الرسائل المرتبطة بالمحادثة

    class Meta:
        model = Chat
        fields = ['id', 'customer', 'merchant', 'created_at', 'updated_at', 'is_active', 'messages']

    def get_messages(self, obj):
        messages = obj.messages.all().order_by('-created_at')  # الرسائل مرتبة من الأحدث إلى الأقدم
        return MessageSerializer(messages, many=True).data
    

class ChatDetailSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name_store')
    store_image = serializers.SerializerMethodField()
    messages = MMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['store_name', 'store_image', 'messages']

    def get_store_image(self, obj):
        if obj.store.image:
            return self.context['request'].build_absolute_uri(obj.store.image.url)
        return None        





class finalChatSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    store_name = serializers.CharField(source='store.name_store', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = Chat
        fields = [
            'id', 'customer', 'owner', 'store',
            'store_name', 'owner_name', 'customer_name',
            'is_active', 'created_at', 'updated_at', 'messages'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'messages', 'store_name', 'owner_name', 'customer_name']

    def get_messages(self, obj):
        messages = obj.messages.all().order_by('created_at')
        return finalMessageSerializer(messages, many=True).data if messages.exists() else []


class finalMessageSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', '', 'text', 'timestamp']
        read_only_fields = ['id', 'created_at', 'sender_name']


class FinaLLlMessageSerializer(serializers.ModelSerializer):
    senderName = serializers.CharField(source='sender.username', read_only=True)
    senderId = serializers.IntegerField(source='sender.id', read_only=True)
    class Meta:
        model = finalMessage
        fields = ['id', 'chat', 'senderName','senderId', 'text', 'timestamp']
        read_only_fields = ['id', 'timestamp']






class ChatListSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name_store', read_only=True)
    store_image = serializers.ImageField(source='store.image', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    

    class Meta:
        model = Chat
        fields = [
            'id', 'customer_name', 'owner_name', 'store_name', 
            'store_image', 'created_at', 'updated_at'
        ]


            