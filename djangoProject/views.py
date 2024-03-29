from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from common.models import Products
from common.models import ShopProducts
from common.models import ProductCategories
from django.contrib.auth import logout
from django.shortcuts import redirect


def home(request):
    products = ShopProducts.objects.all()
    paginator = Paginator(products, 24)  # 假设每页显示多少个商品

    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表
    context = {
        'products': paged_products,
    }
    return render(request, '首页.html',context)


def logout_view(request):
    logout(request)  # Django的logout函数会结束用户的session
    return redirect('home')  # 将用户重定向到登录页面或者首页

def get_products(request):
    category_id = request.GET.get('category_id')
    if category_id is not None:
        types = ProductCategories.objects.filter(category_id=category_id).values_list('category_id', flat=True)
        ids = Products.objects.filter(p_type__in=types).values_list('p_id', flat=True)
        shoppro = ShopProducts.objects.filter(product_id__in=ids)
    else:
        # 如果没有接收到 category_id 参数，就获取所有商品
        shoppro = ShopProducts.objects.all()
    products2 = Products.objects.all()

    # 检查用户是否已经登录
    if 'u_id' in request.session:
        # 如果用户已经登录，就渲染 userpage.html 模板
        template_name = 'userpage.html'
    else:
        # 如果用户没有登录，就渲染 首页.html 模板
        template_name = '首页.html'

    content = render_to_string(template_name, {'products': shoppro,'products2':products2})
    return HttpResponse(content)