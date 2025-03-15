from django.urls import path
from .views import AddEvaluationView, StoreReviews, UpdateReviewView

urlpatterns = [
    path('store/<int:store_id>/add-evaluation/', AddEvaluationView.as_view(), name='add_evaluation'),
    path('stores/<int:store_id>/reviews/', StoreReviews.as_view(), name='store-reviews'),
    path('store/<int:store_id>/edit-evaluation/<int:review_id>/', UpdateReviewView.as_view(), name='edit_review'),
]
