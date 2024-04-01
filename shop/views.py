from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string

from common.models import ShopProducts, ProductCategories, Products


# Create your views here.
# 商家页面
def shoppage(request):
    # 从会话中获取用户的ID
    u_id = request.session.get('u_id')
    shop_products = ShopProducts.objects.filter(shop__s_id=u_id)
    paginator = Paginator(shop_products, 3)  # 假设每页显示多少个商品
    products = Products.objects.all()
    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    u_id = request.session.get('u_id')
    role = request.session.get('role')

    context = {
        'shop_products': paged_products,
        'products': products,
        'user_id': u_id,
        'role': role
    }
    return render(request, 'shoppage.html', context)


def myproducts(request):
    # 从会话中获取用户的ID
    u_id = request.session.get('u_id')
    # 从GET请求中获取类别ID
    category_id = request.GET.get('category_id')
    if category_id is not None and category_id != '0':
        types = ProductCategories.objects.filter(category_id=category_id).values_list('category_id', flat=True)
        ids = Products.objects.filter(p_type__in=types).values_list('p_id', flat=True)
        shop_products = ShopProducts.objects.filter(shop__s_id=u_id, product_id__in=ids)
    else:
        # 如果没有接收到 category_id 参数，就获取这个u_id商家的全部商品
        shop_products = ShopProducts.objects.filter(shop__s_id=u_id)

    products = Products.objects.all()

    # 创建一个 Paginator 对象，每页显示 24 个商品
    paginator = Paginator(shop_products, 3)
    # 从 GET 请求的查询参数中获取页码
    page = request.GET.get('page')
    # 使用 Paginator 对象的 get_page 方法来获取当前页的商品
    shop_products = paginator.get_page(page)

    # 检查用户是否已经登录
    if 'u_id' in request.session:
        # 如果用户已经登录
        template_name = 'shop_my_products.html'
    else:
        # 如果用户没有登录，就渲染 首页.html 模板
        template_name = '首页.html'

    content = render_to_string(template_name,
                               {'shop_products': shop_products, 'products': products, 'category_id': category_id})
    return HttpResponse(content)


def shop_productdetails(request, p_id):
    u_id = request.session.get('u_id')
    role = request.session.get('role')
    shop_product = ShopProducts.objects.get(shop_product_id=p_id)
    products = Products.objects.get(p_id=shop_product.product_id)
    return render(request, 'shop_product_details.html',
                  {'shop_product': shop_product, 'products': products, 'u_id': u_id, 'role': role})

def manage_products(request):
    # 从会话中获取用户的ID
    u_id = request.session.get('u_id')
    category_id = request.GET.get('category_id')
    if category_id is not None and category_id != '0':
        types = ProductCategories.objects.filter(category_id=category_id).values_list('category_id', flat=True)
        ids = Products.objects.filter(p_type__in=types).values_list('p_id', flat=True)
        shop_products = ShopProducts.objects.filter(shop__s_id=u_id, product_id__in=ids)
    else:
        # 如果没有接收到 category_id 参数，就获取这个u_id商家的全部商品
        shop_products = ShopProducts.objects.filter(shop__s_id=u_id)
    paginator = Paginator(shop_products, 3)  # 假设每页显示多少个商品
    products = Products.objects.all()
    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    context = {
        'shop_products': paged_products,
        'products': products,
        'user_id': u_id,
    }
    return render(request, 'shop_manage_products.html', context)


def edit_product(request, product_id):
    product = get_object_or_404(ShopProducts, pk=product_id)
    if request.method == "POST":
        # 这里处理表单提交的数据，更新产品信息
        # 可以使用ModelForm或直接从request.POST中获取数据并更新
        return redirect('shop_manage_products')  # 保存后重定向回管理商品页面
    else:
        # GET请求时显示带有产品信息的编辑表单
        return render(request, 'shop_edit_product.html', {'product': product})


def delete_product(request):
    return None

def product_detail(request):
    return None

def shop_order(request):
    return render(request, 'shop_order.html')


def sales_analysis(request):
    return render(request, 'shop_sales_analysis.html')


