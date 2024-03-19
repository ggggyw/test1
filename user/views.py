from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from login_register.models import ShopProducts
from login_register.models import Products
from login_register.models import Carts


# Create your views here.
def userspage(request):
    products = ShopProducts.objects.all()  # 获取所有商品对象
    products2= Products.objects.all()
    context = {'products': products,
               'products2':products2}  # 构建上下文字典
    return render(request, 'userpage.html',context)

def userprofile(request):
    return render(request, 'userprofile.html')

def usercart(request):
    return render(request,'usercart.html')


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    user_id=request.POST.get('user_id')
    products = ShopProducts.objects.filter(product_id=product_id).first()
    products2 = Products.objects.filter(p_id=product_id).first()
    quantity = int(request.POST.get('quantity', 1))
    shop_id=products.shop_id

    # 获取或创建购物车项
    cart, created = Carts.objects.get_or_create(
        product_id=product_id,
        user_id=user_id,
        shop_id=shop_id,
        defaults={'quantity': 0,
                  'join_time':'2023-03-19 00:00'}
    )

    # 更新数量
    cart.quantity += quantity
    cart.join_time = timezone.now()
    cart.save()
    # 网页跳转问题，如何动态添加，暂时还没想好真的要用javascript吗？
    return render(request,'productdetails.html',{'product': products,'products2':products2})

def userorder(request):
    return render(request,'userorder.html')
def userserve(request):
    return render(request,'userserve.html')
def product_details(request, p_id):
    product = ShopProducts.objects.get(shop_product_id=p_id)
    products2 = Products.objects.get(p_id=product.product_id)
    return render(request, 'productdetails.html', {'product': product,'products2':products2})