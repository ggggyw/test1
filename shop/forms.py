# forms.py
from django import forms
from django.core.exceptions import ValidationError

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
    product_auditstatus = forms.CharField(
        initial='待审核',
        widget=forms.HiddenInput(),  # 这会渲染成一个不可见的 input 字段
    )
    discount = forms.DecimalField(max_digits=10, decimal_places=2)  # 设置最大位数和小数位数
    class Meta:
        model = ShopProducts
        fields = [ 'product_desc', 'product_status', 'stock_quantity',
                  'original_price', 'discount', 'product_auditstatus']

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')

        # 检查折扣是否在0到1的范围内，但不能等于1
        if discount is not None and (discount <= 0 or discount > 1):
            raise ValidationError('折扣必须在0到1的范围内，不能等于0')

        return discount
    def clean(self):
        cleaned_data = super().clean()
        # 获取原始价格和折扣
        original_price = cleaned_data.get('original_price')
        discount = cleaned_data.get('discount')

        # 计算当前价格
        if original_price is not None and discount is not None:
            current_price = original_price * (discount )
            current_price = round(current_price, 2)  # 四舍五入到两位小数
            cleaned_data['current_price'] = current_price

        return cleaned_data
    def __init__(self, *args, **kwargs):
        super(ShopProductForm, self).__init__(*args, **kwargs)
        # 保留其他自定义标签设置
        self.fields['product_desc'].label = "商品描述"
        self.fields['stock_quantity'].label = "库存数量"
        self.fields['original_price'].label = "原始价格"
        self.fields['discount'].label = "商品折扣"
        self.fields['product_auditstatus'].label = "审核状态"
        # 商品状态的自定义标签已在上面通过ChoiceField设置
