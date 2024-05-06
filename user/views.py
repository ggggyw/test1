from datetime import timedelta

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, F, Prefetch
from django.http import HttpResponse, JsonResponse
import json

from django.views.decorators.csrf import csrf_exempt

from common.models import ShopProducts, Users, Carts, Shops, Admin, Orders, OrderDetails,Followers,ProductCategories
from common.models import Products
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from django.contrib import messages

# Create your views here.
def userpage(request):

    products = ShopProducts.objects.exclude(product_status='下架').filter(product_auditstatus__in=['审核通过'])
    products2 = Products.objects.all()
    paginator = Paginator(products, 24)  # 假设每页显示多少个商品

    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    u_id = request.session.get('u_id')
    role = request.session.get('role')

    context = {
        'products': paged_products,
        'products2':products2,
        'user_id': u_id,
        'role': role
    }
    return render(request, 'userpage.html', context)

def get_goods_list(request):
    category_id = request.GET.get('category_id', 0)
    products = ShopProducts.objects.filter(product__p_type__category_id=category_id).filter(product_auditstatus__in=['审核通过']).order_by('shop_product_id')
    products2 = Products.objects.all()
    paginator = Paginator(products, 24)  # 假设每页显示多少个商品

    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    context = {
        'products': paged_products,
        'products2': products2,
        'category_id': category_id
    }
    return render(request, 'goods_list.html', context)
def userprofile(request):
    context = {}
    u_id = request.session.get('u_id')
    role = request.session.get('role')
    pending_orders_count = Orders.objects.filter(user_id=u_id, status='待付款').count()
    shipped_orders_count = Orders.objects.filter(user_id=u_id, status='待收货').count()
    if role == 'user':
        # 获取并处理用户信息
        user = get_object_or_404(Users, u_id=u_id)
        context = {
            'u_id': user.u_id,
            'u_acc': user.u_acc,
            'u_name': user.u_name,
            'u_psw': user.u_psw,
            'u_sex': user.u_sex,
            'u_phone': user.u_phone,
            'email': user.email,
            'created_at': user.created_at,
            'role': role,
            'pending_orders_count': pending_orders_count,
            'shipped_orders_count': shipped_orders_count,
        }
    return render(request, 'userprofile.html', context)

def edit_userprofile(request):
    context = {}
    u_id = request.session.get('u_id')
    role = request.session.get('role')
    if role == 'user':
        user = get_object_or_404(Users, u_id=u_id)
        if request.method == 'POST':
            # 处理表单提交
            user.u_name = request.POST.get('u_name')
            user.u_psw = request.POST.get('u_psw')
            user.u_sex = request.POST.get('u_sex')
            user.u_phone = request.POST.get('u_phone')
            user.email = request.POST.get('email')
            user.save()
            return redirect('userprofile')
        else:
            # 显示表单
            context = {
                'user': user,
                'role': role,
            }
    return render(request, 'edit_userprofile.html', context)

def usercart(request):
    cart=Carts.objects.all()
    shopproduct=ShopProducts.objects.all()
    product=Products.objects.all()
    u_id = request.session.get('u_id')
    context={
        'cart': cart,
        'shoppro':shopproduct,
        'pro':product,
        'uid':u_id
    }
    return render(request,'usercart.html',context)

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

@require_POST
def add_to_cart(request):
   product_id = request.POST.get('product_id')
   user_id = request.POST.get('user_id')
   if user_id is None or user_id == 'None':
       return JsonResponse({'error': '请先登录'})
   user_id = int(user_id)  # 尝试将 user_id 转换为整数
   shop_product = ShopProducts.objects.get(shop_product_id=product_id)
   product = Products.objects.get(p_id=shop_product.product_id)
   quantity = int(request.POST.get('quantity', 1))
   shop_id = shop_product.shop_id

   # 获取或创建购物车项
   cart, created = Carts.objects.get_or_create(
       product_id=product_id,
       user_id=user_id,
       shop_id=shop_id,
       defaults={'quantity': 0, 'join_time': timezone.now()}
   )

   # 更新数量
   cart.quantity += quantity
   cart.join_time = timezone.now()
   cart.save()

   # 根据具体情况返回 JSON 或重定向
   return JsonResponse({'success': True})


from django.core.paginator import Paginator
def userorder(request):
    ord_de=OrderDetails.objects.all()
    u_id = request.session.get('u_id')
    orders=Orders.objects.filter(user_id=u_id)
    now = timezone.now()
    # 对每个订单进行检查
    for order in orders:
        # 如果订单未支付且从下单时间起已超过3天，则取消订单
        if order.status == '待付款':
            time_diff = order.paid_time - order.o_time
            if time_diff > timedelta(days=3):
                order.status = '已取消'  # 设置状态为 "已取消"
                order.save()
    orders = Orders.objects.filter(user_id=u_id)
    order_ids = [order.o_id for order in orders]
    context={
        'orders':orders,
        'ord_de':ord_de,
        'u_id':u_id,
        'order_ids':order_ids
    }
    return render(request,'userorder.html',context)
def order_page(request):
    return render(request, 'userorderpage.html')
def userserve(request):
    return render(request,'userserve.html')

from django.db.models import Q
import random

def product_details(request, p_id):
    u_id = request.session.get('u_id')
    role = request.session.get('role')
    product = ShopProducts.objects.get(shop_product_id=p_id)
    products2 = Products.objects.get(p_id=product.product_id)

    # 获取该商品所属的店铺
    shop = product.shop

    is_following = False
    if u_id:
        try:
            user = Users.objects.get(u_id=u_id)
            # 检查用户是否关注该店铺
            is_following = Followers.objects.filter(u=user, s=shop).exists()
        except Users.DoesNotExist:
            pass

    # 获取当前商品的名称
    current_product_name = products2.p_name


    # 使用当前商品名称作为关键字搜索相关商品
    related_products = ShopProducts.objects.filter(
        Q(product__p_name__icontains=current_product_name) |
        Q(product_desc__icontains=current_product_name)
    ).select_related('product', 'shop').exclude(shop_product_id=p_id)

    # 随机选择4个相关商品作为推荐商品
    recommend_products = random.sample(list(related_products), min(8, len(related_products)))


    return render(request, 'productdetails.html',
                  {'product': product, 'products2': products2, 'u_id': u_id, 'role': role,
                   'is_following': is_following, 'store_name': shop.s_name, 'shop': shop,
                   'recommend_products': recommend_products})

def delete_item(request):
    # print(request.body)
    if request.method == 'POST':
        request_data = json.loads(request.body)
        item_id = request_data.get('item_id')
        # print(item_id)
        u_id=request.session.get('u_id')
        cart=Carts.objects.all()
        cart.filter(product_id=item_id,user_id=u_id).delete()
        return JsonResponse({'message': 'Item deleted successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'})


def checkout(request):
    # 地址输入有问题
    if request.method == 'POST':
        request_data = json.loads(request.body)
        selected_product_ids = request_data.get('selectedProductIds')
        address = request_data.get('address')
        address_text = request_data.get('address')
        # print(address_text)
        u_id = request.session.get('u_id')
        itemPrices = request_data.get('itemPrices')
        totalPrice = request_data.get('totalPrice')
        itemQuantities = request_data.get('itemQuantities')

        try:
            # 检查地址是否存在，如果不存在，则创建新地址
            address_obj, created = UserAddresses.objects.get_or_create(
                user_id=u_id,
                address=address_text,
                defaults={'is_default': False}  # 如果需要其他默认值，可以在此处设置
            )
            # 从购物车表中删除选中的商品
            Carts.objects.filter(product_id__in=selected_product_ids, user_id=u_id).delete()

            # 减少库存量
            ShopProducts.objects.filter(product_id__in=selected_product_ids).update(
                stock_quantity=F('stock_quantity') - 1
            )

            # 创建新订单
            new_order = Orders.objects.create(
                status='1', paid_time='1999-01-01 00:00:00',
                o_time=timezone.localtime(timezone.now()),
                total_price=totalPrice, user_id=u_id, order_address=address
            )

            # 在订单详情表中添加选中的商品详情
            for i, product_id in enumerate(selected_product_ids):
                OrderDetails.objects.create(
                    quantity=itemQuantities[i],
                    current_single_price=itemPrices[i],
                    order_id=new_order.o_id,
                    product_id=product_id,
                    shop_id=1  # 假设shop_id是已知的
                )

            return JsonResponse({'success': True, 'message': '结算成功', 'order_id': new_order.o_id})
        except Exception as e:
            # 在实务中，应当记录这个异常
            return JsonResponse({'success': False, 'message': '结算失败'})

def payment(request):
    return render(request, 'userpayment_page.html')

@csrf_exempt
def process_payment(request):
    # 从请求中获取支付数据
    data = json.loads(request.body)
    order_id = data['order_id']  # 获取请求中的订单 ID
    # 获取当前的时间
    current_time = timezone.now()
    # 更新订单状态和时间
    Orders.objects.filter(o_id=order_id).update(status="待发货", paid_time=current_time)
    return JsonResponse({'success': True, 'message': '支付成功'})


def update_quantity(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        cart_id = request_data.get('cart_id')
        new_quantity = request_data.get('newQuantity')

        # 首先检查 new_quantity 是否为正数
        if new_quantity is not None and new_quantity < 1:
            return JsonResponse({'success': False, 'message': '数量不可为负数或零'})

        try:
            # 更新数据库中对应商品的数量
            product = Carts.objects.get(id=cart_id)
            product.quantity = new_quantity
            product.save()
            return JsonResponse({'success': True, 'message': '数量已更新'})
        except Carts.DoesNotExist:
            return JsonResponse({'success': False, 'message': '商品不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': '更新失败'})

#以下再次购买逻辑有问题------------------------------------------------应该根据status决定是否应该再次购买
# --应连同前面一并修改
@csrf_exempt
def again_buy(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        products = data.get('products', [])
        u_id = request.session.get('u_id')
        for product in products:
            product_id=product.get('product_id')
            shop_product = ShopProducts.objects.get(shop_product_id=product_id)
            shop_id = shop_product.shop_id
            cart, created = Carts.objects.get_or_create(
                product_id=product_id,
                user_id=u_id,
                shop_id=shop_id,
                defaults={'quantity': 0, 'join_time': timezone.now()}
            )
            # 更新数量
            cart.quantity += 1
            cart.join_time = timezone.now()
            cart.save()

        return JsonResponse({'message': '添加到购物车'}, status=200)
    else:
        return JsonResponse({'error': '请求方法不支持'}, status=400)

@csrf_exempt
def confirm_receipt(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            order = Orders.objects.get(o_id=data['o_id'])
            order.status = '已收货'
            order.save()
            return JsonResponse({'success': True, 'message': '订单状态已更新为已完成。'})
        except Orders.DoesNotExist:
            return JsonResponse({'success': False, 'message': '该订单不存在。'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': '服务器错误。', 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'message': '无效的请求方法。'})

@csrf_exempt
def confirm(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            order = Orders.objects.get(o_id=data['o_id'])
            order.status = '已完成'  # 假设 '已完成' 是完成状态的正确值
            order.save()
            return JsonResponse({'success': True, 'message': '订单状态已更新为已完成。'})
        except Orders.DoesNotExist:
            return JsonResponse({'success': False, 'message': '该订单不存在。'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': '服务器错误。', 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'message': '无效的请求方法。'})

@require_POST
def return_order(request):
    data = json.loads(request.body)
    order_id = data.get('o_id')
    try:
        order = Orders.objects.get(o_id=order_id)
        order.status = '待退货'
        order.save()
        return JsonResponse({'success': True, 'message': '退货成功。'})
    except Orders.DoesNotExist:
        return JsonResponse({'success': False, 'message': '订单不存在。'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': '服务器错误。', 'error': str(e)})

@csrf_exempt
def delete_order(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        order_id = data.get('order_id', {})
        order = Orders.objects.filter(o_id=order_id).first()

        if order:
            if order.status == '已取消':
                order.status = 0
                order.save()
            else:
                order.status = '已取消'
                order.save()

            return JsonResponse({'message': '删除成功'}, status=200)
        else:
            return JsonResponse({'error': '订单不存在'}, status=404)
    else:
        return JsonResponse({'error': '删除失败'}, status=400)


def user_orders(request):
    user_id = request.session.get('u_id')
    page = request.GET.get('page', 1)  # 获取页码
    page_size = 5  # 定义每页多少个订单

    # 订单状态的映射，这个根据你的具体需求来设定
    status_mapping = {
        'all': None,
        'pending': '待付款',
        'shipped': '待收货',
        'beshipped': '待发货',
        'ship': '已收货',
        'review': '已完成',
        'bereturned': '待退货',
        'returned': '已退货',
        'recycle': '已取消'
    }
    status = request.GET.get('status')
    status_value = status_mapping.get(status, None)

    try:
        if status_value:
            orders = Orders.objects.filter(user_id=user_id, status=status_value).exclude(status='0')
        else:
            orders = Orders.objects.filter(user_id=user_id).exclude(status='0')

        # 应用分页
        paginator = Paginator(orders, page_size)
        try:
            orders_page = paginator.page(page)
        except PageNotAnInteger:
            orders_page = paginator.page(1)
        except EmptyPage:
            orders_page = paginator.page(paginator.num_pages)

        orders_data = [{
            'order_id': order.o_id,
            'order_details': [{
                'product_name': Products.objects.get(p_id=detail.product.product_id).p_name,
                'product_image_url': detail.product.product_image_url,
                'quantity': detail.quantity,
                'price': detail.current_single_price,
                'product_id': detail.product_id
            } for detail in order.orderdetails_set.all()],
            'total_amount': order.total_price,
            'status': order.status,
            'user_id': order.user_id,
            'user_name':Users.objects.get(u_id=user_id).u_name
        } for order in orders_page]

        pagination_data = {
            'has_previous': orders_page.has_previous(),
            'has_next': orders_page.has_next(),
            'num_pages': paginator.num_pages,
            'current_page': orders_page.number
        }

        return JsonResponse({'orders': orders_data, 'pagination': pagination_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])  # 只处理HTTP POST请求
def get_user_info(request):
    data = json.loads(request.body)
    user_id = data.get('uid')
    # 从数据库中获取用户信息
    user = Users.objects.get(u_id=user_id)
    addresses = UserAddresses.objects.filter(user__u_id=user_id).all()
    address_list = [
        {
            'address': address.address
        } for address in addresses
    ]
    if user:  # 确定用户存在
        # 创建一个字典来保存和返回用户信息
        user_info = {
            'u_name': user.u_name,
            'u_sex': user.u_sex,
            'u_phone': user.u_phone,
            'email': user.email,
            'address':address_list
        }
        # 使用JsonResponse返回JSON数据
        return JsonResponse(user_info)
    else:
        return JsonResponse({'error': 'User not found'}, status=404)


from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.db import IntegrityError
@require_POST
def follow_shop(request, shop_id):
    shop = get_object_or_404(Shops, pk=shop_id)
    user = get_object_or_404(Users, u_id=request.session.get('u_id'))
    try:
        Followers.objects.create(u=user, s=shop, created_at=timezone.now())
    except IntegrityError:
        pass
    return JsonResponse({'success': True})

@require_POST
def unfollow_shop(request, shop_id):
    shop = get_object_or_404(Shops, pk=shop_id)
    user = get_object_or_404(Users, u_id=request.session.get('u_id'))
    Followers.objects.filter(u=user, s=shop).delete()
    return JsonResponse({'success': True})

def search_products(request):
    query = request.GET.get('q')
    if query:
        products = ShopProducts.objects.filter(
            Q(product__p_name__icontains=query) |
            Q(product_desc__icontains=query)
        ).select_related('product', 'shop')
    else:
        products = ShopProducts.objects.none()

    context = {'products': products, 'query': query}
    return render(request, 'search_results.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from common.models import Users, UserAddresses


def address_management(request):
    user_id = request.session.get('u_id')
    user = get_object_or_404(Users, u_id=user_id)

    default_address = UserAddresses.objects.filter(user=user, is_default=True).first()
    other_addresses = UserAddresses.objects.filter(user=user, is_default=False)

    if default_address is None:
        #插入默认地址为"默认地址"
        default_address = UserAddresses.objects.create(user=user, address='默认地址', is_default=True)
    if not default_address and other_addresses.count() == 1:
        only_address = other_addresses.first()
        only_address.is_default = True
        only_address.save()
        default_address = only_address
        other_addresses = UserAddresses.objects.none()

    if request.method == 'POST':
        default_address_id = request.POST.get('default_address_id')
        if default_address_id:
            default_address.address = default_address_id
            default_address.save()

        for address in other_addresses:
            address_id = address.address_id
            updated_address = request.POST.get(f'address_{address_id}')
            if updated_address:
                address.address = updated_address
                address.save()

        new_address = request.POST.get('new_address')
        if new_address:
            new_address_obj = UserAddresses.objects.create(user=user, address=new_address)
            if not default_address:
                new_address_obj.is_default = True
                new_address_obj.save()

        return redirect('address_management')

    context = {
        'default_address': default_address,
        'other_addresses': other_addresses,
    }

    return render(request, 'edit_useradress.html', context)




def set_default_address(request, address_id):
    user_id = request.session.get('u_id')
    user = get_object_or_404(Users, u_id=user_id)

    address = get_object_or_404(UserAddresses, address_id=address_id)

    address.is_default = True
    address.save()

    UserAddresses.objects.filter(user=user).exclude(address_id=address_id).update(is_default=False)

    return redirect('address_management')



def delete_address(request, address_id):
    address = get_object_or_404(UserAddresses, address_id=address_id)
    address.delete()

    return redirect('address_management')

def follow_page(request):
    user_id = request.session.get('u_id')
    user = get_object_or_404(Users, u_id=user_id)
    followers = Followers.objects.filter(u=user)
    shops = [follower.s for follower in followers]
    all_shops = Shops.objects.all()
    #随机选12个商品
    products = ShopProducts.objects.filter(shop__in=shops).order_by('?')[:8]
    return render(request, 'user_shops_follows.html', {'shops': shops, 'products': products, 'all_shops': all_shops})

def shop_details(request, shop_id):
    shop = get_object_or_404(Shops, pk=shop_id)
    products = ShopProducts.objects.filter(shop=shop)
    return render(request, 'shop_details.html', {'shop': shop, 'products': products})

def chat(request, shop_id):
    shop_product_id=request.GET.get('product')
    product = ShopProducts.objects.get(shop_product_id=shop_product_id)
    product_det=Products.objects.get(p_id=product.product_id)
    shop= get_object_or_404(Shops, pk=shop_id)
    return render(request, 'chat.html', { 'shop': shop, 'product': product_det, 'product_base': product})