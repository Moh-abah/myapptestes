from rest_framework.exceptions import ValidationError
from .models import Review, Store


def add_evaluation_to_store(customer, store_id, rating, comment):
    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        raise ValidationError("المتجر غير موجود.")

    # التحقق من وجود تقييم سابق لنفس العميل
    if Review.objects.filter(customer=customer, store=store).exists():
        raise ValidationError("لقد قمت بتقييم هذا المتجر مسبقًا.")

    # إنشاء التقييم
    Review.objects.create(customer=customer, store=store, rating=rating, comment=comment)
