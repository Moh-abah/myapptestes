from django.db import models
from stores.models import Store
from users.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviewss')  # التقييمات الخاصة بالعملاء
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='reviews')  # العلاقة مع المتجر
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # تقييم من 1 إلى 5
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} rated {self.store.name_store} ({self.rating} stars)"
    
    class Meta:
        unique_together = ('customer', 'store')
