from django.db.models import Q
from .models import Store

class StoreService:

    def create_store(user, store_data):
        # منطق لإنشاء المتجر (إذا كنت تحتاجه في مكان آخر)
        store = Store.objects.create(owner=user, **store_data)
        return store
    @staticmethod
    def get_store_by_id(store_id):
        try:
            store = Store.objects.get(id=store_id)
            return store
        except Store.DoesNotExist:
            return None

    @staticmethod
    def search_stores(query):
        # البحث في المتاجر باستخدام اسم المتجر أو نوعه أو الفئة
        return Store.objects.filter(
            Q(name_store__icontains=query) | Q(subcategory__icontains=query) | Q(category__icontains=query)
        )
