# forms.py
from django import forms
from common.models import ShopProducts, ProductCategories, Products


class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['p_name', 'p_type', 'brand']


class ShopProductForm(forms.ModelForm):
    class Meta:
        model = ShopProducts
        fields = ['product_desc', 'product_status', 'stock_quantity',
                  'original_price', 'discount', 'current_price']
