from django.apps import AppConfig
from django.conf import settings
from django.db import models
from django.forms import ValidationError


class Store(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stores',
        limit_choices_to={"user_type": "merchant"}  # فقط التجار يمكنهم إنشاء متجر
    )

    """
    # الفئات الرئيسية
    CATEGORY_CHOICES = [
        ('food', 'فئة المواد الغذائية'),
        ('fashion', 'فئة الأزياء والملابس والأحذية'),
        ('electronics', 'فئة الإلكترونيات والأجهزة'),
        ('furniture', 'فئة الأثاث والديكور'),
        ('health_beauty', 'فئة الصحة والجمال'),
        ('home_kitchen', 'فئة الأدوات المنزلية والمطبخ'),
        ('  ', 'فئة المجوهرات والإكسسوارات'),
        ('gifts_books', 'فئة الهدايا والمكتبات'),
        ('construction', 'فئة البناء وموادها'),
        ('automotive', 'فئة السيارات وملحقاتها'),
    ]

    # الأنواع الفرعية لكل فئة
    SUBCATEGORY_CHOICES = {
        'food': [
            ('fruits_veggies', 'متاجر الخضروات والفواكه'),
            ('meat_fish', 'متاجر اللحوم والأسماك والدواجن'),
            ('spices_nuts', 'متاجر التوابل والمكسرات'),
            ('general_food', 'مواد غذائية'),
        ],
        'fashion': [
            ('shoes', 'متاجر الأحذية'),
            ('clothing_design', 'متاجر الملابس الجاهزة وتصميمها (رجالي ونسائي)'),
        ],
        'electronics': [
            ('computers', 'متاجر الحواسيب وملحقاتها'),
            ('smartphones', 'متاجر الهواتف الذكية والإكسسوارات'),
            ('smart_devices', 'متاجر الأدوات الذكية'),
            ('gaming', 'متاجر الألعاب الإلكترونية وأجهزة الكونسول'),
        ],
        'furniture': [
            ('office_furniture', 'متاجر الأثاث المكتبي'),
            ('decor', 'متاجر الديكور'),
            ('bedroom_carpets', 'متاجر غرف النوم والمجالس والسجاد'),
        ],
        'health_beauty': [
            ('skincare', 'متاجر العناية بالبشرة'),
            ('perfumes', 'متاجر العطور'),
        ],
        'home_kitchen': [
            ('cleaning_supplies', 'متاجر المنظفات المنزلية'),
            ('kitchen_furniture', 'متاجر الأثاث المطبخي'),
            ('cooking_tools', 'متاجر أدوات الطهي'),
        ],
        'jewelry_accessories': [
            ('gold_jewelry', 'متاجر المجوهرات الذهبية'),
            ('general_accessories', 'متاجر الإكسسوارات العادية'),
        ],
        'gifts_books': [
            ('gifts', 'متاجر الهدايا'),
            ('bookstore', 'المكتبات'),
        ],
        'construction': [
            ('electric_tools', 'الأدوات الكهربائية ومواد ومعدات البناء'),
            ('iron', 'متاجر الحديد'),
            ('wood', 'متاجر الخشب'),
            ('cement', 'متاجر الإسمنت'),
            ('aggregates', 'متاجر الكري والنيس'),
        ],
        'automotive': [
            ('car_sales', 'متجر بيع السيارات'),
            ('car_rental', 'متجر تأجير السيارات'),
            ('new_parts', 'متاجر قطع الغيار الجديدة'),
            ('used_parts', 'متاجر قطع الغيار المستخدم والتشليح'),
            ('car_accessories', 'متاجر إكسسوارات السيارات'),
            ('tires_oil', 'متاجر الإطارات والزيوت'),
        ],
    }
    """
    name_store = models.CharField(max_length=100)
    category = models.CharField(max_length=50, null=True, blank=True)
    subcategory = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)  # إضافة حقل الوصف
    location = models.JSONField(default=dict)  # حفظ الإحداثيات
    images = models.JSONField()  # قائمة الصور
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    """ 
    def clean(self):
        
        التحقق من صحة الفئة الفرعية بناءً على الفئة الرئيسية.
        
        if self.category and self.subcategory:
            valid_subcategories = dict(self.SUBCATEGORY_CHOICES).get(self.category, [])
            if self.subcategory and self.subcategory not in [sub[0] for sub in valid_subcategories]:
                raise ValueError(f"Subcategory '{self.subcategory}' is not valid for category '{self.category}'.")
            
    """
    def clean(self):
        if not self.location or 'latitude' not in self.location or 'longitude' not in self.location:
            raise ValidationError("Location must include both latitude and longitude.")
        
        
    def save(self, *args, **kwargs):
        self.clean()  # التأكد من صحة البيانات قبل الحفظ
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_store
    