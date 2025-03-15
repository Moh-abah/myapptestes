from django.urls import path
from .views import CreateStoreView, GetStoresByMerchantView, StoreDetailByUserView, StoreListView, StoreDetailsView, SearchStoresView

urlpatterns = [
    path('create/', CreateStoreView.as_view(), name='create_store'),
    path('', StoreListView.as_view(), name='store_list'),  
    path('<int:store_id>/', StoreDetailsView.as_view(), name='store_details'),
    path('search/', SearchStoresView.as_view(), name='search_stores'),
    path('stordash/<int:merchant_id>/', GetStoresByMerchantView.as_view(), name='store-detail-by-user'),
    path('stordata/<int:user_id>/', StoreDetailsView.as_view(), name='stordata'),
]
