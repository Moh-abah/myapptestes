from asyncio.log import logger
import logging
from urllib import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from stores.models import Store
from users.models import CustomUser
from .serializers import StoreSerializer, StoreSearchSerializer,CStoreSerializer,UserSerializer
from .services import StoreService
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication



logger = logging.getLogger(__name__)

class StoreListView(APIView):
    def get(self, request):
        """
        عرض جميع المتاجر المتاحة في النظام.
        """
        stores = Store.objects.prefetch_related('reviews')  # جلب جميع المتاجر
        serializer = StoreSerializer(stores, many=True)
        logger.info(f"Stores data: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)

class StoreDetailsView(APIView):
    def get(self, request, store_id):
        """
        عرض تفاصيل متجر بناءً على معرف المتجر.
        """
        store = StoreService.get_store_by_id(store_id)
        if store:   
            serializer = StoreSerializer(store)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Store not found."}, status=status.HTTP_404_NOT_FOUND)

class SearchStoresView(APIView):
    def get(self, request):
        """
        البحث عن المتاجر باستخدام اسم المتجر أو الفئة أو النوع.
        """
        query = request.query_params.get('q')  # الكلمات التي أدخلها العميل
        serializer = StoreSearchSerializer(data={'query': query})
        
        if serializer.is_valid():
            stores = StoreService.search_stores(serializer.validated_data['query'])
            return Response(stores, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IsMerchant(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.user_type == 'merchant':
                return True
            else:
                print(f"User type is not 'merchant', it's {request.user.user_type}")  # طباعة نوع المستخدم
                return False
        return False

class CreateStoreView(APIView):
    permission_classes = [IsAuthenticated, IsMerchant]  # السماح فقط للمستخدمين المتحقق منهم من نوع "تاجر"
    authentication_classes = [JWTAuthentication]  # استخدام JWT للمصادقة
    
    def post(self, request):
        logger.error(f"Request Headers: {request.headers}") # طباعة ترويسات الطلب
        logger.error(f"Request User: {request.user}") # طباعة المستخدم
        if request.user.user_type != 'merchant':
            return Response({"error": "You do not have permission to create a store."}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        data['owner'] = request.user.id  # إضافة معرف المستخدم كمالك للمتجر

        serializer = CStoreSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StoreOwnerListView(APIView):
    permission_classes = [IsAuthenticated]  # التأكد من أن المستخدم مسجل

    def get(self, request):
        """
        عرض المتاجر التي يمتلكها التاجر.
        """
        stores = Store.objects.filter(owner=request.user)  # جلب المتاجر الخاصة بالتاجر
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class StoreDetailByUserView(APIView):
    permission_classes = [IsAuthenticated]  # التأكد من أن المستخدم موثوق به
    serializer_class = StoreSerializer  # ربط السيريالايزر الذي يعرض بيانات المتجر

    def get_object(self):
        user_id = self.kwargs['user_id']  # الحصول على user_id من المعاملات في URL
        try:
            store = Store.objects.get(owner__id=user_id)  # جلب المتجر بناءً على ID المالك
            return store
        except Store.DoesNotExist:
            return None  # أو يمكن رفع خطأ إذا لم يتم العثور على المتجر 
        
class GetStoresByMerchantView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, merchant_id):
        try:
            stores = Store.objects.filter(owner_id=merchant_id)
            if not stores.exists():
                return Response({"message": "لم يتم العثور على متاجر لهذا التاجر"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = StoreSerializer(stores, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)