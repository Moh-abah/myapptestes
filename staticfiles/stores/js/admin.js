document.addEventListener('DOMContentLoaded', function () {
    const categoryField = document.getElementById('id_category');
    const subcategoryField = document.getElementById('id_subcategory');

    function updateSubcategoryOptions() {
        const selectedCategory = categoryField.value;
        const subcategoryChoices = {
            'food': [
                ['fruits_veggies', 'متاجر الخضروات والفواكه'],
                ['meat_fish', 'متاجر اللحوم والأسماك والدواجن'],
                ['spices_nuts', 'متاجر التوابل والمكسرات'],
                ['general_food', 'مواد غذائية'],
            ],
            'fashion': [
                ['shoes', 'متاجر الأحذية'],
                ['clothing_design', 'متاجر الملابس الجاهزة وتصميمها (رجالي ونسائي)'],
            ],
            // أضف بقية الفئات الفرعية هنا
        };

        // تنظيف الخيارات الحالية
        subcategoryField.innerHTML = '';

        if (selectedCategory && subcategoryChoices[selectedCategory]) {
            subcategoryChoices[selectedCategory].forEach(function (subcat) {
                const option = document.createElement('option');
                option.value = subcat[0];
                option.textContent = subcat[1];
                subcategoryField.appendChild(option);
            });
        }
    }

    // عندما يتغير الاختيار في حقل الفئة الرئيسية، قم بتحديث الخيارات في الفئة الفرعية
    categoryField.addEventListener('change', updateSubcategoryOptions);

    // قم بتحديث الفئات الفرعية عند تحميل الصفحة لأول مرة
    updateSubcategoryOptions();
});
