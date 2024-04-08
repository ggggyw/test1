# forms.py
from django import forms
from common.models import ShopProducts, ProductCategories, Products


class ProductForm(forms.ModelForm):
    # 用ModelChoiceField替代ChoiceField，并设置queryset
    p_type = forms.ModelChoiceField(
        queryset=ProductCategories.objects.all(),  # 获取所有的产品类别实例
        empty_label="选择商品类型",  # 可以设置一个空白的选择提示，作为下拉菜单的第一项
        label='商品类型',
        to_field_name='category_id'  # 指定p_type字段应该匹配ProductCategories表中的id字段
    )

    class Meta:
        model = Products
        fields = ['p_name', 'p_type', 'brand']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # 设置自定义标签
        self.fields['p_name'].label = "商品名称"
        self.fields['p_type'].label = "商品类型"
        self.fields['brand'].label = "品牌名称"


class ShopProductForm(forms.ModelForm):
    # 定义商品状态的选项
    STATUS_CHOICES = (
        ('上架', '上架'),  # 第一个值是存储在数据库中的实际值，第二个值是在表单上显示的友好名称
        ('下架', '下架')
    )

    product_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label="商品状态",
    )

    product_image = forms.ImageField(required=False, label="商品图片")

    class Meta:
        model = ShopProducts
        fields = ['product_image', 'product_desc', 'product_status', 'stock_quantity',
                  'original_price', 'discount', 'current_price']

    def __init__(self, *args, **kwargs):
        super(ShopProductForm, self).__init__(*args, **kwargs)
        # 保留其他自定义标签设置
        self.fields['product_desc'].label = "商品描述"
        self.fields['stock_quantity'].label = "库存数量"
        self.fields['original_price'].label = "原始价格"
        self.fields['discount'].label = "折扣"
        self.fields['current_price'].label = "现价"
        # 商品状态的自定义标签已在上面通过ChoiceField设置
