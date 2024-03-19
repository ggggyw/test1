from django.shortcuts import render
from common.models import ShopProducts
from common.models import Products


# Create your views here.
def userspage(request, user_id):
    products = ShopProducts.objects.all()  # 获取所有商品对象
    products2 = Products.objects.all()
    context = {
        'products': products,
        'products2': products2,
        'user_id': user_id  # 添加 user_id 到上下文
    }
    return render(request, 'userspage.html', context)  # 将上下文传递给模板

def userprofile(request):
    return render(request, 'userprofile.html')

def usercart(request):
    return render(request,'usercart.html')

def product_details(request, p_id):
    product = ShopProducts.objects.get(shop_product_id=p_id)
    products2 = Products.objects.get(p_id=product.product_id)
    return render(request, 'productdetails.html', {'product': product,'products2':products2})