from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from common.models import Products
from common.models import ShopProducts
from common.models import ProductCategories



def home(request):
    products = ShopProducts.objects.all()  # 获取所有商品对象
    products2= Products.objects.all()
    context = {'products': products,
               'products2':products2}  # 构建上下文字典
    return render(request, '首页.html',context)

def get_products(request):
    category_id = request.GET.get('category_id')
    types = ProductCategories.objects.filter(category_id=category_id).values_list('category_id', flat=True)
    ids = Products.objects.filter(p_type__in=types).values_list('p_id', flat=True)
    shoppro = ShopProducts.objects.filter(product_id__in=ids)
    products2 = Products.objects.all()
    content = render_to_string('首页.html', {'products': shoppro,'products2':products2})
    return HttpResponse(content)
