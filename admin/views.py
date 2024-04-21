from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from common.models import Admin, Users,Shops,ShopProducts,Orders,OrderDetails,Products
from django.core.paginator import Paginator


def adminpage(request):
    # 如果没有登陆，那么重定向到登陆页面
    if 'ad_id' not in request.session:
        return redirect('login')

    admin = Admin.objects.get(ad_id=request.session['ad_id'])
    users = Users.objects.all()
    shops = Shops.objects.all()
    orders_all = Orders.objects.all()
    order_details = OrderDetails.objects.all()
    products = Products.objects.all()
    shop_products = ShopProducts.objects.all()

    paginator_users = Paginator(users, 6)  # 每页显示 6 个用户
    user_page_number = request.GET.get('user_page')
    user_page_obj = paginator_users.get_page(user_page_number)

    paginator_shops = Paginator(shops, 6)  # 每页显示 6 个商店
    shop_page_number = request.GET.get('shop_page')
    shop_page_obj = paginator_shops.get_page(shop_page_number)

    paginator_products = Paginator(shop_products, 6)  # 每页显示 6 个商品
    product_page_number = request.GET.get('product_page')
    product_page_obj = paginator_products.get_page(product_page_number)

    paginator_orders = Paginator(orders_all, 6)  # 每页显示 6 个订单
    order_page_number = request.GET.get('order_page')
    orders = paginator_orders.get_page(order_page_number)

    context = {
        'admin': admin,
        'is_super': admin.is_super,
        'users': user_page_obj,
        'shops': shop_page_obj,
        'orders': orders,  # 这里只传入当前页的订单
        'order_details': order_details,
        'products': products,
        'shop_products': product_page_obj,
    }
    return render(request, 'adminpage.html', context)


@csrf_exempt
def get_admin_info(request):
    if request.method == 'POST':
        ad_id = request.POST.get('ad_id')
        try:
            admin = Admin.objects.get(ad_id=ad_id)  # 从数据库获取管理员对象
            data = {
              'ad_id': admin.ad_id,
              'ad_acc': admin.ad_acc,
              'ad_psw': admin.ad_psw,
              'is_super': admin.is_super,
            }
            return JsonResponse({'success': True, 'data': data})
        except Admin.DoesNotExist:
            return JsonResponse({'success': False, 'error': '管理员不存在'})
    else:
        return JsonResponse({'success': False, 'error': '无效的请求'})