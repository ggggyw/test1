from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods, require_POST
import json
from common.models import Admin, Users,Shops,ShopProducts,Orders,OrderDetails,Products
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

def adminpage(request):
    # 如果没有登陆，那么重定向到登陆页面
    if 'ad_id' not in request.session:
        return redirect('login')

    admin = Admin.objects.get(ad_id=request.session['ad_id'])
    is_super=admin.is_super
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

    adminn = Admin.objects.exclude(is_super=1)
    paginator_ad = Paginator(adminn, 6)  # 每页显示 6 个用户
    admin_page_number = request.GET.get('admin_page')
    admin_page_obj = paginator_ad.get_page(admin_page_number)

    context = {
        'admin': admin,
        'users': user_page_obj,
        'shops': shop_page_obj,
        'orders': orders,  # 这里只传入当前页的订单
        'order_details': order_details,
        'products': products,
        'shop_products': product_page_obj,
        'admins':admin_page_obj,
        'is_super':is_super
    }
    return render(request, 'adminpage.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def create_admin(request):
    # 从请求体获取数据
    try:
        data = json.loads(request.body)
        ad_acc = data.get('admin_acc')
        ad_psw = data.get('admin_psw')
        is_super = 0  # 默认值为 False

        # 输入验证（作为示例）
        if not ad_acc or not ad_psw:
            return JsonResponse({'success': False, 'msg': '用户名和密码为必填项'})

        # 检查用户名是否已存在
        if Admin.objects.filter(ad_acc=ad_acc).exists():
            return JsonResponse({'success': False, 'msg': '该用户名已存在'})

        # 创建管理员
        Admin.objects.create(ad_acc=ad_acc, ad_psw=ad_psw, is_super=is_super)

        return JsonResponse({'success': True, 'msg': '管理员创建成功'})
    except Exception as e:
        return JsonResponse({'success': False, 'msg': f'发生错误: {str(e)}'})

@csrf_exempt  # 如果你的前端请求包含了有效的 CSRF 令牌，这行不是必需的
def get_order_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            o_id = data.get('o_id')

            order = Orders.objects.get(o_id=o_id)
            order_info = {
                'user_id': order.user_id,
                'status': order.status,
                'paid_time': order.paid_time.strftime('%Y-%m-%d %H:%M:%S') if order.paid_time else None,
                'o_time': order.o_time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_price': order.total_price,
                'order_address': order.order_address,
                'o_id':o_id
            }
            print(order_info)
            return JsonResponse({'success': True, 'data': order_info})
        except Orders.DoesNotExist:
            return JsonResponse({'success': False, 'message': '订单不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': '请求处理错误', 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'message': '无效的请求方法'}, status=405)

@csrf_exempt
def update_order_info(request):
    """
    View to update order information.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            o_id = data.get('o_id')
            status = data.get('status')
            paid_time = data.get('paid_time')
            order_address = data.get('order_address')

            order = get_object_or_404(Orders, pk=o_id)
            if status:
                order.status = status
            if paid_time:
                order.paid_time = parse_datetime(paid_time)
            if order_address:
                order.order_address = order_address
            order.save()

            return JsonResponse({'success': True, 'message': '订单信息更新成功！'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

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


@require_http_methods(["POST"])
@csrf_exempt
def get_users_info(request):
    # 检查用户ID是否被提交
    user_id = request.POST.get('u_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': '缺少用户ID参数'})

    try:
        # 使用get()查询数据库以获取用户信息
        user = Users.objects.get(u_id=user_id)

        # 返回用户信息
        user_info = {
            'u_id': user.u_id,
            'u_acc': user.u_acc,
            'u_name': user.u_name,
            'u_sex': user.u_sex,
            'u_phone': user.u_phone,
            'email': user.email,
            # 'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')  # 如果需要的话格式化日期
        }
        return JsonResponse({'success': True, 'data': user_info})
    except Users.DoesNotExist:
        # 如果没找到用户，返回错误
        return JsonResponse({'success': False, 'message': '用户不存在'})
    except Exception as e:
        # 捕获其他异常
        return JsonResponse({'success': False, 'message': '服务器错误', 'error': str(e)})


@require_POST  # 确保只接受 POST 请求
@csrf_exempt
def update_user_info(request):
    try:
        data = json.loads(request.body)
        u_id = data.get('u_id')
        u_acc = data.get('u_acc')
        u_name = data.get('u_name')
        u_sex = data.get('u_sex')
        u_phone = data.get('u_phone')
        email = data.get('email')


        # 根据 u_id 查找用户并更新信息
        user = Users.objects.get(u_id=u_id)
        user.u_acc = u_acc
        user.u_name = u_name
        user.u_sex=u_sex
        user.u_phone=u_phone
        user.email=email

        user.save()

        # 返回成功响应
        return JsonResponse({'success': True, 'message': '用户信息已更新'})

    except Users.DoesNotExist:
        # 如果找不到用户
        return JsonResponse({'success': False, 'message': '未找到用户'})
    except json.JSONDecodeError:
        # 如果请求体不是有效的 JSON
        return JsonResponse({'success': False, 'message': '无效的 JSON 数据'})
    except Exception as e:
        # 捕获并处理任何其他异常
        return JsonResponse({'success': False, 'message': '更新过程中出错', 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def update_shop_info(request):
    try:
        # 解析请求体获取数据
        data = json.loads(request.body)
        s_id = data.get('s_id')
        s_name = data.get('s_name')
        s_acc = data.get('s_acc')
        s_phone = data.get('s_phone')
        email = data.get('email')
        address = data.get('address')

        # 获取要更新的商家对象
        shop = Shops.objects.get(s_id=s_id)

        # 更新商家信息
        shop.s_name = s_name
        shop.s_acc = s_acc
        # shop.s_psw = data.get('s_psw')  # 如果需要更新密码
        shop.s_phone = s_phone
        shop.email = email
        shop.address = address

        # 保存更改
        shop.save()

        # 返回成功响应
        return JsonResponse({'success': True, 'message': '商家信息更新成功'})

    except Shops.DoesNotExist:
        # 如果找不到商家
        return JsonResponse({'success': False, 'message': '商家不存在'})
    except Exception as e:
        # 捕获并响应其他异常
        return JsonResponse({'success': False, 'message': '更新失败', 'error': str(e)})

@require_http_methods(["GET"])
def order_items(request, order_id):
    try:
        order_details = OrderDetails.objects.filter(order_id=order_id).select_related('product', 'shop')
        items_data = [{
            'order_detail_id': detail.order_detail_id,
            'product_id': detail.product_id,
            'product_name': Products.objects.get(p_id=detail.product.product_id).p_name,
            'product_image_url': detail.product.product_image_url,
            'shop_id': detail.shop_id,
            'shop_name': detail.shop.s_name,
            'quantity': detail.quantity,
            'current_single_price': detail.current_single_price
        } for detail in order_details]

        return JsonResponse({'success': True, 'order_items': items_data})
    except Orders.DoesNotExist:
        return JsonResponse({'success': False, 'error': '订单不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

from django.utils import timezone
@csrf_exempt
@require_http_methods(["POST"])
def createuser(request):
    # 将请求体中的JSON数据解析为Python字典
    data = json.loads(request.body)
    user_acc = data.get('user_acc')
    user_name = data.get('user_name')
    user_sex = data.get('user_sex')
    user_phone = data.get('user_phone')
    user_email = data.get('user_email')
    u_psw = data.get('u_psw', '')  # 假设用户密码字段可选，为简单起见设为''若未提供
    time=timezone.now()
    # 使用获取的数据创建用户实例
    try:
        user = Users(
            u_acc=user_acc,
            u_name=user_name,
            u_sex=user_sex,
            u_phone=user_phone,
            email=user_email,
            u_psw=u_psw,
            created_at=time
        )
        user.save()  # 保存用户到数据库
        # 返回成功状态和信息
        return JsonResponse({'success': True, 'msg': '用户创建成功'})
    except Exception as e:
        # 处理错误、例如用户账户名已存在等
        return JsonResponse({'success': False, 'msg': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def createshop(request):
    try:
        data = json.loads(request.body)
        print(data)
        shop_name = data.get('shop_name')
        shop_acc = data.get('shop_acc')
        s_psw = data.get('s_psw')
        shop_phone = data.get('shop_phone')
        shop_email = data.get('shop_email')
        shop_address = data.get('shop_address')

        # 这里可能需要执行一些验证逻辑，例如检查账号是否已存在等。

        # 创建商家对象并保存到数据库
        shop = Shops(
            s_name=shop_name,
            s_acc=shop_acc,
            s_psw=s_psw,
            s_phone=shop_phone,
            email=shop_email,
            address=shop_address
        )
        shop.save()

        return JsonResponse({'success': True, 'msg': '商家创建成功'})
    except Exception as e:
        return JsonResponse({'success': False, 'msg': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def delete_user(request):
    try:
        data = json.loads(request.body)
        u_id = data['u_id']
        user = Users.objects.get(u_id=u_id)
        user.delete()
        return JsonResponse({'success': True, 'message': '用户已删除'})
    except Users.DoesNotExist:
        return JsonResponse({'success': False, 'message': '用户不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': '删除过程出错', 'error': str(e)})

@csrf_exempt
def delete_shop(request):
    try:
        data = json.loads(request.body)
        s_id = data.get('s_id')
        shop = Shops.objects.get(s_id=s_id)
        shop.delete()
        return JsonResponse({'success': True, 'message': '商家删除成功'})

    except Shops.DoesNotExist:
        return JsonResponse({'success': False, 'message': '商家不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': '删除失败: ' + str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def get_product_info(request):
    try:
        # 解析请求体中的 JSON 数据
        data = json.loads(request.body)
        print(data)
        shop_product_id = data.get('product_id')  # 这里改为 shop_product_id
        print(shop_product_id)
        # 使用 shop_product_id 查询商品信息
        shop_product = ShopProducts.objects.get(shop_product_id=shop_product_id)

        # 构建响应数据
        product_info = {
            'shop_product_id': shop_product.shop_product_id,
            'product_desc': shop_product.product_desc,
            'product_status': shop_product.get_product_status_display(),  # 获取可读的状态
            'product_auditstatus': shop_product.get_product_auditstatus_display(),  # 获取可读的审核状态
            'product_image_url': shop_product.product_image_url,
            'stock_quantity': shop_product.stock_quantity,
            'original_price': shop_product.original_price,
            'discount': shop_product.discount if shop_product.discount is not None else "",
            'current_price': shop_product.current_price if shop_product.current_price is not None else "",
        }

        # 返回 JSON 响应
        return JsonResponse({'success': True, 'data': product_info})

    except ShopProducts.DoesNotExist:
        print('aaaa')
        return JsonResponse({'success': False, 'error': 'Product does not exist'})
    except Exception as e:
        print('asdasd')
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def update_product_info(request):
    try:
        data = json.loads(request.body)

        shop_product_id = data.get('shop_product_id')
        product = ShopProducts.objects.get(shop_product_id=shop_product_id)

        # 使用原价和折扣来计算现价
        original_price = data.get('original_price')
        discount = data.get('discount')

        # 确保原价和折扣都提供了
        if original_price is not None and discount is not None:
            # 转换为 float 方便计算（在生产中可能需要更复杂的精度处理）
            original_price_float = float(original_price)
            discount_float = float(discount)

            # 计算现价，保留两位小数
            current_price_float = original_price_float * (1 - discount_float / 100)

            # 更新商品信息
            product.product_desc = data.get('product_desc')
            product.product_status = data.get('product_status')
            product.product_auditstatus = data.get('product_auditstatus')
            product.product_image_url = data.get('product_image_url')
            product.stock_quantity = data.get('stock_quantity')
            product.original_price = original_price_float
            product.discount = discount_float
            product.current_price = round(current_price_float, 2)

            # 如果审核状态为“审核不通过”，则商品状态自动设为“下架”
            if product.product_auditstatus == "审核不通过":
                product.product_status = "下架"

            product.save()
            return JsonResponse({'success': True, 'message': '商品信息更新成功'})
        else:
            return JsonResponse({'success': False, 'message': '必须提供原价和折扣'})

    except ShopProducts.DoesNotExist:
        return JsonResponse({'success': False, 'message': '商品不存在'})
    except ValueError:
        return JsonResponse({'success': False, 'message': '无效的数值输入'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': '服务器错误', 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def delete_product(request):
    try:
        data = json.loads(request.body)
        shop_product_id = data.get('shop_product_id')

        # 在库存商品表中查找并删除商品
        product = ShopProducts.objects.get(shop_product_id=shop_product_id)
        product.delete()

        return JsonResponse({'success': True, 'message': '商品删除成功'})
    except ShopProducts.DoesNotExist:
        return JsonResponse({'success': False, 'message': '商品不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': '服务器错误', 'error': str(e)})

@csrf_exempt  # 如果全局启用了CSRF保护，可能需要此装饰器来允许从前端进行POST请求
@require_http_methods(["POST"])
def delete_admin(request):
    try:
        data = json.loads(request.body)
        admin_id = data.get('ad_id')
        admin = Admin.objects.get(ad_id=admin_id)
        admin.delete()
        return JsonResponse({'success': True, 'message': '管理员删除成功'}, status=200)
    except Admin.DoesNotExist:
        return JsonResponse({'success': False, 'message': '管理员不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])
@csrf_exempt  # 如果你的前端不处理 CSRF token，可以暂时放宽 CSRF 限制
def get_shop_info(request):
    try:
        # 解析请求体中的 JSON 数据
        data = json.loads(request.body)
        s_id = data.get('s_id')

        # 使用 s_id 查询商家信息
        shop = Shops.objects.get(s_id=s_id)

        # 将商家信息构造成一个字典以便返回
        shop_info = {
            's_id': shop.s_id,
            's_name': shop.s_name,
            's_acc': shop.s_acc,
            's_psw': shop.s_psw,  # 出于安全考虑，通常不应该传输密码
            's_phone': shop.s_phone,
            'email': shop.email,
            'address': shop.address,
        }
        print(shop_info)
        # 返回包含商家信息的 JSON 响应
        return JsonResponse({'success': True, 'data': shop_info})
    except Shops.DoesNotExist:
        # 如果商家不存在，返回错误信息
        return JsonResponse({'success': False, 'message': '商家不存在'})
    except Exception as e:
        # 捕获并处理任何其他异常
        return JsonResponse({'success': False, 'message': '服务器错误', 'error': str(e)})

from common.models import Users
def search_users(request):
    keyword = request.POST.get('keyword')  # 获取搜索关键字

    # 在数据库中搜索包含关键字的用户
    users = Users.objects.filter(
        Q(u_id__icontains=keyword) |
        Q(u_name__icontains=keyword) |
        Q(u_sex__icontains=keyword) |
        Q(u_phone__icontains=keyword) |
        Q(email__icontains=keyword) |
        Q(created_at__icontains=keyword)
    )

    # 将用户数据转换为 JSON 格式
    user_list = list(users.values())

    # 返回 JSON 数据
    return JsonResponse(user_list, safe=False)


from common.models import Shops

def search_shops(request):
    keyword = request.POST.get('keyword')  # 获取搜索关键字

    # 在数据库中搜索包含关键字的商家
    shops = Shops.objects.filter(
        Q(s_id__icontains=keyword) |
        Q(s_name__icontains=keyword) |
        Q(s_acc__icontains=keyword) |
        Q(s_phone__icontains=keyword) |
        Q(email__icontains=keyword) |
        Q(address__icontains=keyword)
    )

    # 将商家数据转换为 JSON 格式
    shop_list = list(shops.values())

    # 返回 JSON 数据
    return JsonResponse(shop_list, safe=False)

from common.models import Orders,ShopProducts
@require_http_methods(["POST"])
def search_products(request):
    keyword = request.POST.get('keyword', '')

    if keyword:
        products = ShopProducts.objects.filter(
            product_auditstatus__icontains=keyword,
            product_status=ShopProducts.ProductStatus.ON_SALE
        ).values(
            'shop_product_id', 'shop_id', 'product_desc', 'product_status',
            'product_auditstatus', 'product_image_url', 'stock_quantity',
            'original_price', 'discount', 'current_price'
        )
        products_list = list(products)
        return JsonResponse({'products': products_list}, safe=False)
    else:
        return JsonResponse({'error': 'No keyword provided'}, status=400)

@require_http_methods(["POST"])
def search_orders(request):
    keyword = request.POST.get('keyword', '')

    if keyword:
        orders = Orders.objects.filter(
            status__icontains=keyword
        ).values(
            'o_id', 'user_id', 'status', 'o_time', 'paid_time',
            'total_price', 'order_address'
        )
        orders_list = list(orders)
        return JsonResponse({'orders': orders_list}, safe=False)
    else:
        return JsonResponse({'error': 'No keyword provided'}, status=400)
@csrf_exempt
@require_http_methods(["POST"])
def update_admin_info(request):
    """
    更新管理员信息
    """
    try:

        data = json.loads(request.body)
        ad_id = data.get('ad_id')
        ad_acc = data.get('ad_acc')
        ad_psw = data.get('ad_psw')
        # 根据 ad_id 查找管理员记录
        admin = Admin.objects.filter(ad_id=ad_id).first()

        if not admin:
            return JsonResponse({'success': False, 'message': '管理员未找到'})

        # 更新管理员信息
        if ad_acc is not None:
            admin.ad_acc = ad_acc
        if ad_psw is not None:
            admin.ad_psw = ad_psw
        # 可以在这里添加更多字段的更新逻辑

        admin.save()  # 保存更新

        return JsonResponse({'success': True, 'message': '管理员信息更新成功'})

    except ValueError:
        return JsonResponse({'success': False, 'message': '无效输入'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': '服务器内部错误'})
