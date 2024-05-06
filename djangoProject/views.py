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
    request.session.clear()
    products = ShopProducts.objects.all()

    # 遍历全部products商品
    for product in products:
        # 如果库存变成了0，就将商品的状态修改为下架
        if product.stock_quantity == 0:
            product.product_status = '下架'
            product.save()  # 保存商品的更改

    paginator = Paginator(products, 24)  # 假设每页显示多少个商品
    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    # 不需要再次查询所有Products，除非有其他用途
    # products2 = Products.objects.all()

    context = {
        'products': paged_products,
        # 'products2': products2  # 如果没有特别用处，这行可以注释掉
    }
    return render(request, '首页.html', context)


def logout_view(request):
    logout(request)  # Django的logout函数会结束用户的session
    return redirect('home')  # 将用户重定向到登录页面或者首页

def get_products(request):
    category_id = request.GET.get('category_id')
    if category_id is not None and category_id != '0':
        types = ProductCategories.objects.filter(category_id=category_id).values_list('category_id', flat=True)
        ids = Products.objects.filter(p_type__in=types).values_list('p_id', flat=True)
        shoppro = ShopProducts.objects.filter(product_id__in=ids)
    else:
        # 如果没有接收到 category_id 参数，或者 category_id 的值为 0，就获取所有商品
        shoppro = ShopProducts.objects.all()
    products2 = Products.objects.all()

    # 创建一个 Paginator 对象，每页显示 24 个商品
    paginator = Paginator(shoppro, 24)
    # 从 GET 请求的查询参数中获取页码
    page = request.GET.get('page')
    # 使用 Paginator 对象的 get_page 方法来获取当前页的商品
    shoppro = paginator.get_page(page)

    # 检查用户是否已经登录
    if 'u_id' in request.session:
        # 如果用户已经登录，就渲染 userpage.html 模板
        template_name = 'userpage.html'
    else:
        # 如果用户没有登录，就渲染 首页.html 模板
        template_name = '首页.html'

    content = render_to_string(template_name, {'products': shoppro,'products2':products2, 'category_id': category_id})
    return HttpResponse(content)


from django.db.models import Q

from django.core.paginator import Paginator


def search_products(request):
    query = request.GET.get('q')
    page_num = request.GET.get('page', 1)

    if query:
        # 使用 p_id 进行搜索
        ids = Products.objects.filter(
            Q(p_name__icontains=query) |
            Q(brand__icontains=query)
        ).values_list('p_id', flat=True)
        shoppro = ShopProducts.objects.filter(product_id__in=ids)

        paginator = Paginator(shoppro, 12)  # 每页显示12个商品
        page_obj = paginator.get_page(page_num)
    else:
        page_obj = ShopProducts.objects.none()

    products2 = Products.objects.all()

    context = {'products': page_obj, 'products2': products2, 'query': query}
    return render(request, 'search_results.html', context)
