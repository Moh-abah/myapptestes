from ast import Store
from django.forms import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import EvaluationSerializer, eeEvaluationSerializer
from .services import add_evaluation_to_store
from .models import Review, Store



class AddEvaluationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, store_id):
        
        serializer = EvaluationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # تمرير البيانات إلى الخدمة
                add_evaluation_to_store(
                    customer=request.user,
                    store_id=store_id,
                    **serializer.validated_data
                )
                return Response({"message": "تم إضافة التقييم بنجاح."}, status=status.HTTP_201_CREATED)

            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # إرجاع الأخطاء من الـ serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UpdateReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id, customer=request.user)  # تأكد من أن التقييم من نفس المستخدم
        except Review.DoesNotExist:
            return Response({"error": "Review not found or not authorized"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EvaluationSerializer(review, data=request.data, partial=True)  # تستخدم `partial=True` للسماح بتعديل بعض الحقول فقط
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class StoreReviews(APIView):
    def get(self, request, store_id):
        try:
            store = Store.objects.get(id=store_id)
            reviews = store.reviews.all()
            serializer = eeEvaluationSerializer(reviews, many=True)
            return Response(serializer.data)
        except Store.DoesNotExist:
            return Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
