from ast import Store
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
import messaging
from rest_framework import generics
from messaging import permissions
from messaging.models import Chat, Message
from messaging.serializers import ChatDetailSerializer, ChatListSerializer, ChatSerializer, ChatWithMessagesSerializer, ChatttrSerializer, FinaLLlMessageSerializer, MessageSerializer, finalChatSerializer, finalMessageSerializer
from messaging.services import create_message, get_merchant_or_404
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging
from .models import Store, finalMessage  # أو إذا كان في مكان آخر
from django.core.exceptions import ObjectDoesNotExist

from users.models import CustomUser

from messaging import models
logger = logging.getLogger(__name__)

User = get_user_model()
"""
class SendMessageView(APIView):
    
    View لإرسال الرسائل من المستخدم الحالي إلى تاجر محدد.
    

    def post(self, request, merchant_id):
        
        معالجة طلب POST لإرسال رسالة.
        
        # تحقق مما إذا كان التاجر ينتمي إلى مجموعة "merchants"
        try:
            merchant = User.objects.get(id=merchant_id)
        except User.DoesNotExist:
            return Response({"error": "التاجر غير موجود."}, status=status.HTTP_404_NOT_FOUND)

        # التحقق من انتماء التاجر إلى مجموعة "merchants"
        if not merchant.groups.filter(name="merchants").exists():
            return Response({"error": "التاجر لا ينتمي إلى مجموعة التجار."}, status=status.HTTP_400_BAD_REQUEST)

        # إضافة معرف المستقبل إلى البيانات
        data = request.data.copy()
        data['receiver'] = merchant_id

        # استخدام Serializer للتحقق
        serializer = MessageSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            # استدعاء الخدمة لإنشاء الرسالة
            create_message(serializer.validated_data, request.user)
            return Response({"message": "تم إرسال الرسالة بنجاح."}, status=status.HTTP_200_OK)

        # إرجاع الأخطاء في حال فشل التحقق
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class GetMessagesWithMerchantView(APIView):
    
    عرض الرسائل بين العميل والتاجر.
    
    def get(self, request, merchant_id):
        user = request.user  # العميل الحالي
        
        # التحقق إذا كان التاجر موجودًا في النظام
        try:
            merchant = User.objects.get(id=merchant_id)
        except User.DoesNotExist:
            return Response({"error": "التاجر غير موجود."}, status=status.HTTP_404_NOT_FOUND)
        
        # التحقق إذا كان التاجر ينتمي لمجموعة "merchants"
        if not merchant.groups.filter(name="merchants").exists():
            return Response({"error": "التاجر لا ينتمي إلى مجموعة التجار."}, status=status.HTTP_400_BAD_REQUEST)

        # استرجاع الرسائل بين العميل والتاجر
        messages = messaging.objects.filter(
            (Q(sender=user) & Q(receiver=merchant)) |
            (Q(sender=merchant) & Q(receiver=user))
        ).order_by('created_at')  # ترتيب الرسائل حسب تاريخ الإرسال

        # تسلسل الرسائل
        serializer = MessageSerializer(messages, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
class GetConversationsView(APIView):
    
    عرض جميع التجار الذين تواصل معهم العميل.
    
    def get(self, request):
        user = request.user  # العميل الحالي
        
        # استرجاع جميع التجار الذين تواصل معهم العميل
        conversations = messaging.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).distinct().values('sender', 'receiver')

        # الحصول على تجار فقط (التأكد من أن المرسل أو المستقبل ينتمي لمجموعة "merchants")
        merchants_ids = set()
        for conversation in conversations:
            if conversation['sender'] != user.id:
                merchants_ids.add(conversation['sender'])
            else:
                merchants_ids.add(conversation['receiver'])
        
        # جلب المستخدمين الذين هم تجار
        merchants = User.objects.filter(id__in=merchants_ids, groups__name="merchants")

        # عرض التجار
        merchant_data = [{"id": merchant.id, "name": merchant.name} for merchant in merchants]
        
        return Response(merchant_data, status=status.HTTP_200_OK)
        
        
"""



class SendMessageView(APIView):

    def post(self, request,chat_id, merchant_id):
        CustomUser = request.CustomUser  # الحصول على المستخدم الحالي
        try:
            # البحث عن المحادثة بين المستخدم والتاجر باستخدام merchant_id
            chat = Chat.objects.get(
                (Q(user1=CustomUser) & Q(user2__id=merchant_id)) | 
                (Q(user1__id=merchant_id) & Q(user2=CustomUser))
            )
        except Chat.DoesNotExist:
            return Response({"detail": "التاجر غير موجود أو لا يوجد لديك محادثة معه."}, status=status.HTTP_404_NOT_FOUND)

        # إذا تم العثور على المحادثة، سنقوم بإنشاء الرسالة
        message = Message.objects.create(
            chat=chat,
            content=request.data['content'],
            sender=CustomUser
        )

        # إرجاع الرسالة التي تم إنشاؤها مع تفاصيلها
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

"""
class SendMessageView(APIView):
    
    إرسال رسالة مع إنشاء المحادثة إذا لم تكن موجودة.
    

    def post(self, request, merchant_id):
        # التحقق من التاجر
        merchant = get_merchant_or_404(merchant_id)
        user = request.user

        # ترتيب المستخدمين
        user1, user2 = (user, merchant) if user.id < merchant.id else (merchant, user)

        # التحقق أو إنشاء المحادثة
        chat, created = Chat.objects.get_or_create(user1=user1, user2=user2)

        # إرسال الرسالة
        data = request.data.copy()
        data['chat'] = chat.id  # ربط الرسالة بالمحادثة
        serializer = MessageSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            message = create_message(serializer.validated_data, user)
            chat.last_message = serializer.validated_data['content']
            chat.save()
            return Response({"message": "تم إرسال الرسالة بنجاح."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        """

class GetMessagesWithMerchantView(APIView):
    def get(self, request, merchant_id):
        user = request.user
        merchant = get_merchant_or_404(merchant_id)

        # محاولة العثور على المحادثة بين العميل والتاجر
        chat = Chat.objects.filter(Q(user1=user, user2=merchant) | Q(user1=merchant, user2=user)).first()

        if not chat:
            return Response({"error": "المحادثة غير موجودة."}, status=status.HTTP_404_NOT_FOUND)

        # استرجاع الرسائل للمحادثة
        messages = Message.objects.filter(chat=chat).order_by('created_at')

        # تسلسل البيانات
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetConversationsView(APIView):
    def get(self, request):
        user = request.user
        
        # استرجاع المحادثات المرتبطة بالمستخدم مع تحسين الأداء باستخدام select_related
        chats = Chat.objects.filter(Q(user1=user) | Q(user2=user))\
            .select_related('user1', 'user2')  # جلب بيانات المستخدمين المرتبطة دفعة واحدة
        
        # استرجاع بيانات المحادثات
        conversations = [
            {
                "id": chat.id,
                "user": {
                    "id": chat.user1.id if chat.user1 != user else chat.user2.id,
                    "name": chat.user1.username if chat.user1 != user else chat.user2.username,
                },
                "last_message": chat.last_message,
                "updated_at": chat.updated_at,
            }
            for chat in chats
        ]

        return Response(conversations, status=status.HTTP_200_OK)


class CreateChatView(APIView):
    def post(self, request):
        user = request.user
        data = request.data
        merchant_id = data.get('merchant_id')

        # جلب التاجر
        merchant = get_merchant_or_404(merchant_id)

        # التحقق من وجود المحادثة
        chat_exists = Chat.objects.filter(
            (Q(user1=user) & Q(user2=merchant)) |
            (Q(user1=merchant) & Q(user2=user))
        ).exists()

        if chat_exists:
            return Response({"error": "المحادثة موجودة بالفعل."}, status=status.HTTP_400_BAD_REQUEST)

        # إنشاء المحادثة
        chat = Chat.objects.create(user1=user, user2=merchant)
        return Response({"message": "تم إنشاء المحادثة بنجاح."}, status=status.HTTP_201_CREATED)



class CheckOrCreateChatView(APIView):

    permission_classes = [IsAuthenticated]  # السماح فقط للمستخدمين المتحقق منهم من نوع "تاجر"
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        customer_id = request.data.get('customer_id')
        merchant_id = request.data.get('merchant_id')

        # تحقق من وجود محادثة بين العميل والتاجر
        chat = Chat.objects.filter(customer_id=customer_id, merchant_id=merchant_id).first()

        if not chat:
            # إذا لم تكن هناك محادثة، قم بإنشاء واحدة جديدة
            chat = Chat.objects.create(customer_id=customer_id, merchant_id=merchant_id)

        return Response({"chat_id": chat.id}, status=status.HTTP_200_OK)
    




class ChattttnewListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        عرض قائمة المحادثات الخاصة بالمستخدم الحالي.
        """
        user = request.user
        # جلب المحادثات التي يكون فيها المستخدم إما عميلًا أو تاجرًا
        chats = Chat.objects.filter(Q(customer=user) | Q(owner=user)).order_by('-updated_at')
        serializer = ChatttrSerializer(chats, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        إنشاء محادثة جديدة.
        """
        # إضافة store_id في البيانات المرسلة من العميل
        merchant_id = request.data.get('merchant_id')
        store_id = request.data.get('store_id')

        # إرسال البيانات عبر الـ Serializer
        serializer = ChatttrSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            chat = serializer.save()
            return Response(ChatttrSerializer(chat, context={'request': request}).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""
# فيو لإدارة قائمة المحادثات وإنشاء محادثة جديدة
class ChatListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # عرض قائمة المحادثات الخاصة بالمستخدم الحالي مع الترتيب حسب updated_at
        user = request.user
        chats = Chat.objects.filter(Q(customer=user) | Q(merchant=user)).order_by('-updated_at')
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # إنشاء محادثة جديدة
        user = request.user  # المستخدم الحالي هو العميل (customer)
        
        # الحصول على معرف التاجر
        merchantId = request.data.get('merchant')
        if not merchantId:
            return Response({"error": "Merchant ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # التأكد من وجود التاجر في النظام
        merchant = get_object_or_404(CustomUser, id=merchantId)
        
        # التحقق من وجود محادثة مسبقة
        existing_chat = Chat.objects.filter(customer=user, merchant_id=merchantId).first()
        if existing_chat:
            return Response(ChatSerializer(existing_chat).data, status=status.HTTP_200_OK)

        # إعداد بيانات المحادثة بدون `last_message`
        chat_data = {
            'customer': user.id,
            'merchant': merchantId,
        }
        
        # استخدام الـ serializer لإنشاء المحادثة
        serializer = ChatSerializer(data=chat_data, context={'request': request})
        
        # التحقق من صحة البيانات
        if serializer.is_valid():
            chat_instance = serializer.save()  # حفظ المحادثة
            
            # إعادة توجيه المستخدم إلى شاشة الرسائل
            # (هنا يجب تحديد منطق إعادة التوجيه في التطبيق الأمامي)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # في حالة وجود أخطاء في البيانات
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        try:
            # إضافة عملية إرسال الرسالة أو إنشاء المحادثة هنا
            # على سبيل المثال:
            message = Message.objects.create(chat_id=chat_id, sender_id=sender_id, receiver_id=receiver_id, content=content)
            logger.info(f"Message sent successfully: {message.id}")
            return Response({"detail": "Message sent successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return Response({"detail": "Error sending message"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""
# فيو لإدارة تفاصيل محادثة معينة (عرض، تحديث، حذف)
class ChatDetailView(APIView):
    permission_classes = [IsAuthenticated, permissions.IsChatParticipant]

    def get_object(self, pk):
        # الحصول على المحادثة أو إرجاع خطأ 404 إذا لم توجد
        try:
            return Chat.objects.get(pk=pk)
        except Chat.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        # عرض تفاصيل محادثة معينة
        chat = self.get_object(pk)
        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        # تحديث محادثة معينة
        chat = self.get_object(pk)
        serializer = ChatSerializer(chat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # حذف محادثة معينة
        chat = self.get_object(pk)
        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# فيو لإدارة قائمة الرسائل وإرسال رسالة جديدة
class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id=None):
        # عرض قائمة الرسائل الخاصة بالمستخدم الحالي مع الترتيب حسب created_at
        user = request.user
        if chat_id:
            messages = Message.objects.filter(chat_id=chat_id, sender=user) | Message.objects.filter(chat_id=chat_id, receiver=user)
        else:
            messages = Message.objects.filter(Q(sender=user) | Q(receiver=user))
        messages = messages.order_by('-created_at')  # ترتيب الرسائل من الأحدث إلى الأقدم
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # إرسال رسالة جديدة
        serializer = MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()  # سيتم تعيين sender تلقائيًا
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# فيو لإدارة تفاصيل رسالة معينة (عرض، تحديث، حذف)
class MessageDetailView(APIView):
    permission_classes = [IsAuthenticated, permissions.IsChatParticipant]

    def get_object(self, pk):
        # الحصول على الرسالة أو إرجاع خطأ 404 إذا لم توجد
        try:
            return Message.objects.get(pk=pk)
        except Message.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        # عرض تفاصيل رسالة معينة
        message = self.get_object(pk)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        # تحديث رسالة معينة
        message = self.get_object(pk)
        serializer = MessageSerializer(message, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # حذف رسالة معينة
        message = self.get_object(pk)
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  
    

class ChatttDetailView(APIView):
    def get(self, request, chat_id):
        messages = Message.objects.filter(chat_id=chat_id).order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    



class ChatDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id=None):
        user = request.user
        if chat_id:
            # جلب محادثة معينة مع الرسائل
            try:
                chat = Chat.objects.get(pk=chat_id, customer=user)  # تأكد أن المستخدم هو العميل
                serializer = ChatWithMessagesSerializer(chat)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Chat.DoesNotExist:
                return Response({"error": "Chat not found or you are not a participant"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # جلب جميع المحادثات مع الرسائل للمستخدم الحالي
            chats = Chat.objects.filter(customer=user)
            serializer = ChatWithMessagesSerializer(chats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        







        
        








































import logging

logger = logging.getLogger(__name__)

class finalCreateChatAPIView(APIView):
    def post(self, request):
        try:
            customer_id = request.data.get('customer')
            owner_id = request.data.get('owner')
            store_id = request.data.get('store')

            if not all([customer_id, owner_id, store_id]):
                return Response({'error': 'Missing required fields (customer, owner, or store)'}, 
                                 status=status.HTTP_400_BAD_REQUEST)

            customer = CustomUser.objects.get(id=customer_id)
            owner = CustomUser.objects.get(id=owner_id)

            try:
                store = Store.objects.get(id=store_id)
            except ObjectDoesNotExist:
                logger.error(f"Store with ID {store_id} does not exist.")
                return Response({'error': 'Invalid store ID'}, status=status.HTTP_400_BAD_REQUEST)

            # التحقق من وجود المحادثة أو إنشائها إذا كانت غير موجودة
            existing_chat = Chat.objects.filter(customer=customer, owner=owner, store=store).first()

            if existing_chat:
                return Response(finalChatSerializer(existing_chat).data, status=status.HTTP_200_OK)
            else:
                chat = Chat.objects.create(
                    customer=customer,
                    owner=owner,
                    store=store,
                    is_active=True  # هذا الحقل مرتبط بـ Chat، وليس Store
                )
                return Response(finalChatSerializer(chat).data, status=status.HTTP_201_CREATED)

        except CustomUser.DoesNotExist as e:
            logger.error(f"Customer or owner not found: {str(e)}")
            return Response({'error': f'Invalid customer or owner ID: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q


from django.db.models import OuterRef, Subquery

class withlastmassegRetrieveChatsAPIView(APIView):
    def get(self, request):
        try:
            # الحصول على user_id من معامل الاستعلام
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response({'error': 'Missing required field: user_id'}, status=status.HTTP_400_BAD_REQUEST)

            # التحقق من وجود المستخدم
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

            # استعلام الرسالة الأخيرة
            last_message_query = finalMessage.objects.filter(chat=OuterRef('pk')).order_by('-timestamp').values('text')[:1]

            # جلب المحادثات بناءً على دور المستخدم مع الرسالة الأخيرة
            if user.user_type == 'customer':
                chats = Chat.objects.filter(customer=user).select_related('store', 'owner').annotate(
                    last_message=Subquery(last_message_query)
                )
            elif user.user_type == 'merchant':
                chats = Chat.objects.filter(owner=user).select_related('store', 'customer').annotate(
                    last_message=Subquery(last_message_query)
                )
            else:
                return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

            # تسلسل بيانات المحادثات
            chat_data = [
                {
                    'chat_id': chat.id,
                    'store_name': chat.store.name_store,  # اسم المتجر كاسم للمحادثة
                    'store_image': chat.store.images if chat.store.images else None,  # صورة المتجر
                    'last_message': chat.last_message,  # آخر رسالة باستخدام Subquery
                    'is_active': chat.is_active,  # حالة النشاط
                    'other_user': {
                        'id': chat.customer.id if user.user_type == 'merchant' else chat.owner.id,
                        'name': chat.customer.name if user.user_type == 'merchant' else chat.owner.name,
                    }
                }
                for chat in chats
            ]

            return Response(chat_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RetrieveChatsAPIView(APIView):
    def get(self, request):
        try:
            # الحصول على user_id من معامل الاستعلام
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response({'error': 'Missing required field: user_id'}, status=status.HTTP_400_BAD_REQUEST)

            # التحقق من وجود المستخدم
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

            # جلب المحادثات بناءً على دور المستخدم
            if user.user_type == 'customer':
                chats = Chat.objects.filter(customer=user).select_related('store', 'owner')
            elif user.user_type == 'merchant':
                chats = Chat.objects.filter(owner=user).select_related('store', 'customer')
            else:
                return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

            # تسلسل بيانات المحادثات
            chat_data = [
                {
                    'chat_id': chat.id,
                    'store_name': chat.store.name_store,  # اسم المتجر كاسم للمحادثة
                    'store_image': chat.store.images if chat.store.images else None,  # صورة المتجر
                    'last_message': chat.messages.last().content if chat.messages.exists() else None,  # آخر رسالة
                    'is_active': chat.is_active,  # حالة النشاط
                    'other_user': {
                        'id': chat.customer.id if user.user_type == 'merchant' else chat.owner.id,
                        'name': chat.customer.name if user.user_type == 'merchant' else chat.owner.name,
                    }
                }
                for chat in chats
            ]

            return Response(chat_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
مع الويب سوكيت في الوقت الفعلي finalSendMessageAPIView
"""
class finalSendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # تسجيل البيانات المستلمة
            logger.info(f"Received data: {request.data}")

            chat_id = request.data.get('chat')
            sender_id = request.data.get('sender')
            text = request.data.get('text')

            # التحقق من وجود الحقول المطلوبة
            if not chat_id or not sender_id:
                logger.warning("Missing 'chat' or 'sender' in request data.")
                return Response(
                    {"error": "Both 'chat' and 'sender' fields are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # جلب كائن المحادثة
            chat = get_object_or_404(Chat, id=chat_id)
            logger.info(f"Chat found with ID: {chat_id}")

            # جلب المرسل
            sender = get_object_or_404(CustomUser, id=sender_id)
            logger.info(f"Sender found with ID: {sender_id}")

            if sender != chat.customer and sender != chat.owner:
                return Response(
                    {"error": "The sender is not a participant in this chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # التحقق من صحة البيانات باستخدام serializer
            serializer = FinaLLlMessageSerializer(data=request.data)
            if serializer.is_valid():
                # حفظ الرسالة
                serializer.save(chat=chat, sender=sender)
                logger.info(f"Message sent successfully in chat {chat_id} by sender {sender_id}.")

                # إرسال الرسالة عبر WebSocket
                channel_layer = get_channel_layer()
                channel_layer.group_send(
                    f'chat_{chat_id}',  # اسم المجموعة بناءً على chat_id
                    {
                        'type': 'chat_message',
                        'message': serializer.data['text'],
                        'sender': sender.username,
                        'timestamp': serializer.data['timestamp']
                    }
                )

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            # تسجيل الأخطاء في serializer
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # تسجيل الاستثناءات مع التفاصيل
            logger.exception(f"An unexpected error occurred: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
        
        """
        بدون الوقت الفعلي ويب سوكيت 
class finalSendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # تسجيل البيانات المستلمة
            logger.info(f"Received data: {request.data}")

            chat_id = request.data.get('chat')
            sender_id = request.data.get('sender')
            text = request.data.get('text')

            # التحقق من وجود الحقول المطلوبة
            if not chat_id or not sender_id:
                logger.warning("Missing 'chat' or 'sender' in request data.")
                return Response(
                    {"error": "Both 'chat' and 'sender' fields are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            

            # جلب كائن المحادثة
            chat = get_object_or_404(Chat, id=chat_id)
            logger.info(f"Chat found with ID: {chat_id}")

            # جلب المرسل
            sender = get_object_or_404(CustomUser, id=sender_id)
            logger.info(f"Sender found with ID: {sender_id}")
            

            if sender != chat.customer and sender != chat.owner:
                return Response(
                    {"error": "The sender is not a participant in this chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            

            # التحقق من أن المرسل عضو في المحادثة
            

            # التحقق من صحة البيانات باستخدام serializer
            serializer = FinaLLlMessageSerializer(data=request.data)
            if serializer.is_valid():
                # حفظ الرسالة
                serializer.save(chat=chat, sender=sender)
                logger.info(f"Message sent successfully in chat {chat_id} by sender {sender_id}.")
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            # تسجيل الأخطاء في serializer
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # تسجيل الاستثناءات مع التفاصيل
            logger.exception(f"An unexpected error occurred: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            """


class FinalGetMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        try:
            logger.debug(f"Received request to fetch messages for chat_id: {chat_id}")

            # الحصول على المحادثة
            chat = get_object_or_404(Chat, id=chat_id)
            logger.debug(f"Chat found: {chat}")

            # التحقق من أن المستخدم مشارك في المحادثة
            if request.user != chat.customer and request.user != chat.owner:
                logger.warning(f"User {request.user} is not authorized to view messages for chat_id: {chat_id}")
                return Response(
                    {"error": "You are not authorized to view messages for this chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # جلب الرسائل المرتبطة بالمحادثة وترتيبها حسب تاريخ الإنشاء
            messages = finalMessage.objects.filter(chat=chat).order_by('timestamp')
            logger.debug(f"Messages fetched from database: {messages}")

            # إذا لم تكن هناك رسائل
            if not messages.exists():
                logger.debug(f"No messages found for chat_id {chat_id}.")
                return Response(
                    {"message": "No messages found for this chat."},
                    status=status.HTTP_200_OK,
                )

            # إضافة logging للتحقق من الرسائل التي تم جلبها
            logger.debug(f"Fetched messages for chat_id {chat_id}: {messages}")

            # تسلسل الرسائل
            serializer = FinaLLlMessageSerializer(messages, many=True)
            logger.debug(f"Serialized data: {serializer.data}")  # سجل شكل البيانات المسلسلة

            # إرجاع الاستجابة
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error while fetching messages: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class MessageList(generics.ListAPIView):
    queryset = finalMessage.objects.all()
    serializer_class = FinaLLlMessageSerializer          

class FinalyGetChatsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # الحصول على المستخدم الحالي
            user = self.request.user

            # جلب جميع المحادثات التي يكون المستخدم جزءًا منها
            chats = Chat.objects.filter(customer=user) | Chat.objects.filter(owner=user)

            # التحقق من وجود محادثات
            if not chats.exists():
                return Response(
                    {"success": False, "message": "No chats found for the current user."},
                    status=status.HTTP_200_OK,
                )

            # تسلسل المحادثات وإرجاع المتجر مع كل محادثة
            serializer = ChatListSerializer(chats, many=True)
            return Response({
                "success": True,
                "message": "Chats fetched successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # تسجيل الأخطاء في السجلات
            logger.error(f"Error fetching chats: {str(e)}")
            return Response(
                {"success": False, "error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )      






     





























































































class getChatsAPIView(APIView):
    def get(self, request, customer_id):
        try:
            chats = Chat.objects.filter(customer_id=customer_id)
            if chats.exists():
                return Response(finalChatSerializer(chats, many=True).data, status=status.HTTP_200_OK)
            return Response({'message': 'No chats found for this customer'}, status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid customer ID'}, status=status.HTTP_400_BAD_REQUEST)
        



class getMessagesAPIView(APIView):
    def get(self, request, chat_id):
        try:
            messages = Message.objects.filter(chat_id=chat_id)
            if messages.exists():
                return Response(finalMessageSerializer(messages, many=True).data, status=status.HTTP_200_OK)
            return Response({'message': 'No messages found for this chat'}, status=status.HTTP_404_NOT_FOUND)
        except Chat.DoesNotExist:
            return Response({'error': 'Invalid chat ID'}, status=status.HTTP_400_BAD_REQUEST)        
        

class finalCheckChatAPIView(APIView):
    def get(self, request, customer_id, store_id):
        try:
            # محاولة الحصول على المحادثة إذا كانت موجودة
            chat = Chat.objects.filter(customer_id=customer_id, store_id=store_id).first()

            if chat:
                # إذا كانت المحادثة موجودة، نرجع البيانات
                return Response({'chat_id': chat.id, 'is_active': chat.is_active}, status=status.HTTP_200_OK)
            else:
                # إذا لم تكن المحادثة موجودة، نقوم بإنشائها
                customer = CustomUser.objects.get(id=customer_id)
                store = Store.objects.get(id=store_id)
                chat = Chat.objects.create(
                    customer=customer,
                    owner=store.owner,  # assuming the store has an owner field
                    store=store,
                    is_active=True
                )
                return Response({'chat_id': chat.id, 'is_active': chat.is_active}, status=status.HTTP_201_CREATED)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid customer ID'}, status=status.HTTP_400_BAD_REQUEST)
        except Store.DoesNotExist:
            return Response({'error': 'Invalid store ID'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)









"""
// file: lib/services/chat_service.dart
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import '../models/finalmasseg.dart';
import '../models/List_Chts.dart';
import '../models/testmodel.dart';

class FinalChatService {
  final String apiUrl = 'http://127.0.0.1:8000/';
  final FlutterSecureStorage _storage = FlutterSecureStorage();

  // الحصول على التوكن من التخزين الآمن
  Future<String?> _getToken() async {
    return await _storage.read(key: 'jwt_token');
  }

  // الدالة المسؤولة عن إضافة التوكن في الـ Headers
  Future<Map<String, String>> _getHeaders() async {
    final token = await _getToken();
    if (token == null) {
      throw Exception('Authorization token is missing');
    }
    return {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };
  }

  // إنشاء محادثة جديدة
  Future<finalmodelChat?> createChat(
      int customerId, int ownerId, int storeId) async {
    final headers = await _getHeaders();
    final response = await http.post(
      Uri.parse('${apiUrl}api/messaging/finalcreate-chat/'),
      headers: headers,
      body: json.encode({
        'customer': customerId,
        'owner': ownerId,
        'store': storeId,
      }),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      final data = json.decode(response.body);
      return finalmodelChat.fromJson(data);
    } else {
      throw Exception('Failed to create chat');
    }
  }

  // إرسال رسالة إلى المحادثة
  Future<FinalMessage> sendMessage(
      int chatId, int senderId, String content) async {
    final headers = await _getHeaders();
    final response = await http.post(
      Uri.parse('${apiUrl}api/messaging/finalsend-message/'),
      headers: headers,
      body: json.encode({
        'chat': chatId,
        'sender': senderId,
        'text': content,
      }),
    );

    if (response.statusCode == 201) {
      final data = jsonDecode(response.body);
      print("Response data: $data"); // Debugging: عرض البيانات
      return FinalMessage.fromJson(data);
    } else {
      throw Exception('Failed to send message');
    }
  }

  // جلب قائمة المحادثات
  Future<List<ListsChat>> fetchChats() async {
    final headers = await _getHeaders();
    final response = await http.get(
      Uri.parse('${apiUrl}api/messaging/GetChatsList/'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['data'] != null) {
        return (data['data'] as List)
            .map((chat) => ListsChat.fromJson(chat))
            .toList();
      } else {
        return [];
      }
    } else {
      throw Exception('Failed to fetch chats');
    }
  }

  // جلب الرسائل للمحادثة
  Future<List<FinalMessage>> getMessages(int chatId) async {
    final headers = await _getHeaders();
    final response = await http.get(
      Uri.parse('${apiUrl}api/messaging/get-messages/$chatId/'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return (data as List)
          .map((message) => FinalMessage.fromJson(message))
          .toList();
    } else {
      throw Exception('Failed to load messages');
    }
  }

  Future<List<chatstest>> fetchChatstest(int userId) async {
    final headers = await _getHeaders();
    final response = await http.get(
        Uri.parse('${apiUrl}api/messaging/chats?user_id=$userId'),
        headers: headers);

    if (response.statusCode == 200) {
      final List data = json.decode(response.body);
      return data.map((chat) => chatstest.fromJson(chat)).toList();
    } else {
      throw Exception('Failed to load chats');
    }
  }
}

"""