from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from .forms import ShopProductForm, ProductForm
from common.models import ShopProducts, ProductCategories, Products, Users, Shops
import pandas as pd
from sqlalchemy import create_engine
from dateutil.relativedelta import relativedelta
from common.models import ShopProducts, ProductCategories, Products, Orders, OrderDetails


# Create your views here.
# 商家页面
def shoppage(request):
    # 从会话中获取用户的ID
    s_id = request.session.get('s_id')
    shop_products = ShopProducts.objects.filter(shop__s_id=s_id)
    paginator = Paginator(shop_products, 8)  # 假设每页显示多少个商品
    products = Products.objects.all()
    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    s_id = request.session.get('u_id')
    role = request.session.get('role')
    category_id = request.GET.get('category_id', 0)

    context = {
        'shop_products': paged_products,
        'products': products,
        's_id': s_id,
        'role': role,
        'category_id': category_id,
    }
    return render(request, 'shoppage.html', context)


def shop_profile(request):
    context = {}
    s_id = request.session.get('s_id')
    role = request.session.get('role')
    if role == 'shop':
        shop = get_object_or_404(Shops, s_id=s_id)
        if s_id:
            # 获取该商家所有的唯一订单ID
            unique_order_ids = OrderDetails.objects.filter(shop__s_id=s_id).values_list('order', flat=True).distinct()

            # 根据这些唯一的订单ID统计每个状态的订单数量
            order_status_counts = Orders.objects.filter(o_id__in=unique_order_ids).values('status').annotate(
                count=Count('status'))

            # 统计该商家所有商品的审核状态数量
            product_audit_status_counts = ShopProducts.objects.filter(shop__s_id=s_id).values(
                'product_auditstatus').annotate(count=Count('product_auditstatus'))
            # 转换查询结果为字典
            status_counts = {status_count['status']: status_count['count'] for status_count in order_status_counts}
            audit_status_counts = {status_count['product_auditstatus']: status_count['count'] for status_count in
                                   product_audit_status_counts}
            context = {
                's_name': shop.s_name,
                's_phone': shop.s_phone,
                'email': shop.email,
                'address': shop.address,
                'order_status_counts': status_counts,
                'product_audit_status_counts': audit_status_counts,
                'role': role,
            }
    return render(request, 'shop_profile.html', context)


def edit_shop_profile(request):
    context = {}
    s_id = request.session.get('s_id')
    role = request.session.get('role')
    if role == 'shop':
        shop = get_object_or_404(Shops, s_id=s_id)
        if request.method == 'POST':
            # 处理表单提交
            shop.s_name = request.POST.get('s_name')
            shop.s_psw = request.POST.get('s_psw')
            shop.s_phone = request.POST.get('s_phone')
            shop.email = request.POST.get('email')
            shop.address = request.POST.get('address')
            shop.save()
            return redirect('edit_shop_profile')
        else:
            # 显示表单
            context = {
                'shop': shop,
                'role': role,
            }
    return render(request, 'edit_shop_profile.html', context)


def myproducts(request):
    # 从会话中获取用户的ID
    s_id = request.session.get('s_id')
    # 从GET请求中获取查询和类别ID
    query = request.GET.get('query', '').strip()
    category_id = request.GET.get('category_id', 0)
    if category_id == 'None':
        category_id = 0
    category_id = int(category_id)
    if query.lower() == 'none' or query == '请输入想找的宝贝':
        query = ''
    # 处理基于查询的商品搜索
    if query is not None and query != '请输入想找的宝贝' and query != '':
        if category_id == 0:
            ids = Products.objects.filter(
                Q(p_name__icontains=query) |
                Q(brand__icontains=query)
            ).values_list('p_id', flat=True)
        else:
            ids = Products.objects.filter(
                (Q(p_name__icontains=query) |
                 Q(brand__icontains=query)) &
                Q(p_type__category_id=category_id)
            ).values_list('p_id', flat=True)
        shop_products = ShopProducts.objects.filter(product_id__in=ids, shop__s_id=s_id)
    else:
        if category_id == 0:
            shop_products = ShopProducts.objects.filter(shop__s_id=s_id)
            query = None
        else:
            shop_products = ShopProducts.objects.filter(shop__s_id=s_id, product__p_type__category_id=category_id)
            query = None

    products = Products.objects.all()

    paginator = Paginator(shop_products, 8)  # 每页显示 8 个商品
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 检查用户是否已经登录
    if 's_id' in request.session:
        template_name = 'shop_my_products.html'
    else:
        template_name = '首页.html'

    context = {'shop_products': page_obj, 'products': products, 'query': query, 'category_id': category_id}
    return render(request, template_name, context)


def shop_productdetails(request, p_id):
    s_id = request.session.get('s_id')
    role = request.session.get('role')
    shop_product = ShopProducts.objects.get(shop_product_id=p_id)
    products = Products.objects.get(p_id=shop_product.product_id)
    category_id = products.p_type.category_id
    return render(request, 'shop_product_details.html',
                  {'shop_product': shop_product, 'products': products, 's_id': s_id, 'role': role , 'category_id': category_id})


def manage_products(request):
    # 从会话中获取用户的ID
    s_id = request.session.get('s_id')
    category_id = request.GET.get('category_id')
    if category_id is not None and category_id != '0' and category_id != '':
        types = ProductCategories.objects.filter(category_id=category_id).values_list('category_id', flat=True)
        ids = Products.objects.filter(p_type__in=types).values_list('p_id', flat=True)
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id, product_id__in=ids)
    else:
        # 如果没有接收到 category_id 参数，就获取这个u_id商家的全部商品
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id)
    paginator = Paginator(shop_products, 3)  # 假设每页显示多少个商品
    products = Products.objects.all()
    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    # 初始化表单实例
    product_form = ProductForm(request.POST or None, request.FILES or None)
    shop_product_form = ShopProductForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        # 获取当前登录的商家ID
        shop_id = request.session.get('s_id')

        # 验证两个表单是否都有效
        if product_form.is_valid() and shop_product_form.is_valid():
            # 保存Products模型实例
            product = product_form.save()

            # 我们需要为ShopProducts设置外键关系
            # 假设ProductForm的save方法返回新创建的Product实例
            shop_product = shop_product_form.save(commit=False)
            shop_product.product = product
            shop_product.shop_id = shop_id
            if 'product_image' in request.FILES:
                myfile = request.FILES['product_image']
                fs = FileSystemStorage(location='static/商品图片')
                filename = fs.save(myfile.name, myfile)
                shop_product.product_image_url = filename
            # 设置current_price字段的值
            shop_product.current_price = shop_product_form.cleaned_data['current_price']
            # 设置product_auditstatus的值为"待审核"
            shop_product.product_auditstatus = '待审核'
            shop_product.save()

            # 向用户显示成功消息并重定向到商品列表页面
            messages.success(request, '商品已成功添加！')
            return redirect('manage_products')  # 这里假设你有一个商品列表的页面
        else:
            messages.error(request, '添加商品时出现错误。')
    else:
        # GET 请求，创建表单并填充当前模型实例数据
        product_form = ProductForm()
        shop_product_form = ShopProductForm()
    context = {
        'shop_products': paged_products,
        'products': products,
        's_id': s_id,
        'category_id': category_id,
        'product_form': product_form,
        'shop_product_form': shop_product_form,
        'query': None
    }
    return render(request, 'shop_manage_products.html', context)


def shop_search_manage_products(request):
    # 为所有可能的搜索字段获取值
    s_id = request.session.get('s_id', None)
    product_name = request.GET.get('product_name', '')
    category_id = request.GET.get('category_id', '0')
    brand = request.GET.get('brand', '')
    description = request.GET.get('description', '')
    status = request.GET.get('status', '')
    audit_status = request.GET.get('audit_status', '')
    max_stock = request.GET.get('max_stock', None)
    min_stock = request.GET.get('min_stock', None)
    min_original_price = request.GET.get('min_original_price', None)
    max_original_price = request.GET.get('max_original_price', None)
    min_discount = request.GET.get('min_discount', None)
    max_discount = request.GET.get('max_discount', None)
    min_current_price = request.GET.get('min_current_price', None)
    max_current_price = request.GET.get('max_current_price', None)

    queryset = ShopProducts.objects.filter(shop__s_id=s_id) if s_id else ShopProducts.objects.none()

    # 构建查询过滤条件
    query_conditions = Q()
    if product_name:
        query_conditions &= Q(product__p_name__icontains=product_name)
    if category_id != '0':
        query_conditions &= Q(product__p_type__category_id=category_id)
    if brand:
        query_conditions &= Q(product__brand__icontains=brand)
    if description:
        query_conditions &= Q(product_desc__icontains=description)
    if status:
        query_conditions &= Q(product_status__iexact=status)
    if audit_status:
        query_conditions &= Q(product_auditstatus__iexact=audit_status)
    if min_stock:
        query_conditions &= Q(stock_quantity__gte=min_stock)
    if max_stock:
        query_conditions &= Q(stock_quantity__lte=max_stock)
    # 调整为处理价格和折扣的范围搜索
    if min_original_price:
        queryset = queryset.filter(original_price__gte=min_original_price)
    if max_original_price:
        queryset = queryset.filter(original_price__lte=max_original_price)
    if min_discount:
        queryset = queryset.filter(discount__gte=min_discount)
    if max_discount:
        queryset = queryset.filter(discount__lte=max_discount)
    if min_current_price:
        queryset = queryset.filter(current_price__gte=min_current_price)
    if max_current_price:
        queryset = queryset.filter(current_price__lte=max_current_price)

    queryset = queryset.filter(query_conditions)
    # 如果查询集为空，添加一条没有找到商品的消息
    if not queryset.exists():
        messages.info(request, '此搜索条件下没有找到商品！')

    paginator = Paginator(queryset, 2)  # 调整页数到10，或其他适合你应用的数字
    page = request.GET.get('page')
    shop_products = paginator.get_page(page)

    # 初始化表单实例
    product_form = ProductForm(request.POST or None, request.FILES or None)
    shop_product_form = ShopProductForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        # 获取当前登录的商家ID
        shop_id = request.session.get('s_id')

        # 验证两个表单是否都有效
        if product_form.is_valid() and shop_product_form.is_valid():
            # 保存Products模型实例
            product = product_form.save()

            # 我们需要为ShopProducts设置外键关系
            # 假设ProductForm的save方法返回新创建的Product实例
            shop_product = shop_product_form.save(commit=False)
            shop_product.product = product
            shop_product.shop_id = shop_id
            if 'product_image' in request.FILES:
                myfile = request.FILES['product_image']
                fs = FileSystemStorage(location='static/商品图片')
                filename = fs.save(myfile.name, myfile)
                shop_product.product_image_url = filename
            # 设置current_price字段的值
            shop_product.current_price = shop_product_form.cleaned_data['current_price']
            # 设置product_auditstatus的值为"待审核"
            shop_product.product_auditstatus = '待审核'
            shop_product.save()

            # 向用户显示成功消息并重定向到商品列表页面
            messages.success(request, '商品已成功添加！')
            return redirect('manage_products')  # 这里假设你有一个商品列表的页面
        else:
            messages.error(request, '添加商品时出现错误。')
    else:
        # GET 请求，创建表单并填充当前模型实例数据
        product_form = ProductForm()
        shop_product_form = ShopProductForm()
    # 将搜索字段回传到模板中，以便保持搜索条件
    context = {
        'shop_products': shop_products,
        'product_name': product_name,
        'category_id': category_id,
        'brand': brand,
        'description': description,
        'status': status,
        'audit_status': audit_status,
        'max_stock': max_stock,
        'min_stock': min_stock,
        'min_original_price': min_original_price,
        'max_original_price': max_original_price,
        'min_discount': min_discount,
        'max_discount': max_discount,
        'min_current_price': min_current_price,
        'max_current_price': max_current_price,
        'product_form': product_form,
        'shop_product_form': shop_product_form,
        'message': '此搜索条件下没有找到商品！' if not shop_products else '',
        'query': None
    }

    return render(request, 'shop_manage_products.html', context)


def edit_product(request, product_id):
    shop_product = get_object_or_404(ShopProducts, pk=product_id)
    product = shop_product.product
    category_id = product.p_type.category_id

    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        shop_product_form = ShopProductForm(request.POST, request.FILES, instance=shop_product)

        if product_form.is_valid() and shop_product_form.is_valid():
            # 更新Products实例
            product_form.save()
            shop_product = shop_product_form.save(commit=False)
            if 'product_image' in request.FILES:
                # 创建一个文件系统存储对象
                fs = FileSystemStorage(location='static/商品图片')
                # 如果已经存在旧的图片，就先删除旧的图片
                if shop_product.product_image_url:
                    fs.delete(shop_product.product_image_url)
                # 保存新的图片
                myfile = request.FILES['product_image']
                filename = fs.save(myfile.name, myfile)
                shop_product.product_image_url = filename
            shop_product.current_price = shop_product_form.cleaned_data['current_price']
            # 设置product_auditstatus的值为"待审核"
            shop_product.product_auditstatus = '待审核'
            shop_product.save()
            # 更新ShopProducts实例
            shop_product_form.save()
            messages.success(request, '修改成功！')
            # 保存后重定向回修改商品页面
            return redirect('edit_product', product_id=product_id)
        else:
            messages.error(request, '修改不成功，请重新修改。')
    else:
        # GET 请求，创建表单并填充当前模型实例数据
        product_form = ProductForm(instance=product)
        shop_product_form = ShopProductForm(instance=shop_product)

    # 将表单传递给模板
    context = {
        'product_form': product_form,
        'shop_product_form': shop_product_form,
        'shop_products': shop_product,
        'products': product,
        'category_id': category_id,
        'query': None
    }
    return render(request, 'shop_edit_product.html', context)


def add_product(request):
    # 初始化表单实例
    product_form = ProductForm(request.POST or None, request.FILES or None)
    shop_product_form = ShopProductForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        # 获取当前登录的商家ID
        shop_id = request.session.get('s_id')

        # 验证两个表单是否都有效
        if product_form.is_valid() and shop_product_form.is_valid():
            # 保存Products模型实例
            product = product_form.save()

            # 我们需要为ShopProducts设置外键关系
            # 假设ProductForm的save方法返回新创建的Product实例
            shop_product = shop_product_form.save(commit=False)
            shop_product.product = product
            shop_product.shop_id = shop_id
            if 'product_image' in request.FILES:
                myfile = request.FILES['product_image']
                fs = FileSystemStorage(location='static/商品图片')
                filename = fs.save(myfile.name, myfile)
                shop_product.product_image_url = filename
            # 设置current_price字段的值
            shop_product.current_price = shop_product_form.cleaned_data['current_price']
            shop_product.save()

            # 向用户显示成功消息并重定向到商品列表页面
            messages.success(request, '商品已成功添加！')
            return redirect('add_product')  # 这里假设你有一个商品列表的页面
        else:
            messages.error(request, '添加商品时出现错误。')
    else:
        # GET 请求，创建表单并填充当前模型实例数据
        product_form = ProductForm()
        shop_product_form = ShopProductForm()

    # 将表单传递给模板
    context = {
        'product_form': product_form,
        'shop_product_form': shop_product_form
    }
    return render(request, 'shop_add_product.html', context)


def delete_product(request, product_id):
    if product_id is not None:
        shop_product = ShopProducts.objects.filter(shop_product_id=product_id).first()
        if shop_product:
            image_path = shop_product.product_image_url  # 获取商品图片的路径
            fs = FileSystemStorage(location='static/商品图片')  # 创建一个文件系统存储对象
            fs.delete(shop_product.product_image_url)  # 删除图片文件
            if fs.exists(shop_product.product_image_url):  # 检查文件是否仍然存在
                print("删除图片错误")  # 如果文件仍然存在，打印一条错误消息
            shop_product.delete()  # 删除对应的商品
    return redirect('manage_products')  # 重定向到manage_products视图


def shop_order(request):
    # 从会话中获取当前登录的商家ID
    shop_id = request.session.get('s_id')

    # 查询这个商家的所有订单
    order_ids = OrderDetails.objects.filter(shop__s_id=shop_id).values_list('order__o_id', flat=True)
    orders = Orders.objects.filter(o_id__in=order_ids)
    # 分页
    paginator = Paginator(orders, 10)  # 例如每页显示10条记录
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    # 将订单传递给模板
    context = {
        'orders': paged_orders,
        'category_id': '0',  # 用于保持搜索条件
        'query': None
    }
    return render(request, 'shop_order.html', context)


def shop_search_orders(request):
    # 为所有可能的搜索字段获取值
    s_id = request.session.get('s_id', None)
    product_name = request.GET.get('product_name', '')
    category_id = request.GET.get('category_id', '0')
    brand = request.GET.get('brand', '')
    description = request.GET.get('description', '')
    status = request.GET.get('status', '')
    audit_status = request.GET.get('audit_status', '')
    max_stock = request.GET.get('max_stock', None)
    min_stock = request.GET.get('min_stock', None)
    min_original_price = request.GET.get('min_original_price', None)
    max_original_price = request.GET.get('max_original_price', None)
    min_discount = request.GET.get('min_discount', None)
    max_discount = request.GET.get('max_discount', None)
    min_current_price = request.GET.get('min_current_price', None)
    max_current_price = request.GET.get('max_current_price', None)

    order_status = request.GET.get('order_status', '')
    min_order_total_price = request.GET.get('min_order_total_price', None)
    max_order_total_price = request.GET.get('max_order_total_price', None)
    min_paid_time = request.GET.get('min_paid_time', None)
    max_paid_time = request.GET.get('max_paid_time', None)
    order_address = request.GET.get('order_address', '')
    min_created_time = request.GET.get('min_created_time', None)
    max_created_time = request.GET.get('max_created_time', None)

    user_name = request.GET.get('user_name', '')
    user_phone = request.GET.get('user_phone', '')
    user_sex = request.GET.get('user_sex', '')
    user_email = request.GET.get('user_email', '')
    # 构建查询条件
    query_conditions = Q()
    # 只展示当前商家(s_id)的订单
    if s_id:
        query_conditions &= Q(orderdetails__shop__s_id=s_id)
        # 假设 'status' 是定义在 Orders 模型中的状态字段
        order_status_counts = Orders.objects.filter(orderdetails__shop__s_id=s_id).values('status').annotate(
            count=Count('status'))
    else:
        order_status_counts = Orders.objects.none()
    if product_name:
        query_conditions &= Q(orderdetails__product__product__p_name__icontains=product_name)
    if category_id != '0':
        query_conditions &= Q(orderdetails__product__product__p_type_id=category_id)
    if brand:
        query_conditions &= Q(orderdetails__product__product__brand__icontains=brand)
    # 注意这里如果其他商家的product名称和商家的product描述相同，这一filter也能提取出其他商家的商品
    if description:
        query_conditions &= Q(orderdetails__product__product_desc__icontains=description)
    if status:  # 注意，这里的字段可能指的是ShopProducts的上架状态
        query_conditions &= Q(orderdetails__product__product_status=status)
    if audit_status:  # 注意，这里可能指的是ShopProducts的审核状态
        query_conditions &= Q(orderdetails__product__product_auditstatus=audit_status)
    if min_stock:
        query_conditions &= Q(orderdetails__product__stock_quantity__gte=min_stock)
    if max_stock:
        query_conditions &= Q(orderdetails__product__stock_quantity__lte=max_stock)
    if min_original_price:
        query_conditions &= Q(orderdetails__product__original_price__gte=min_original_price)
    if max_original_price:
        query_conditions &= Q(orderdetails__product__original_price__lte=max_original_price)
    if min_discount:
        query_conditions &= Q(orderdetails__product__discount__gte=min_discount)
    if max_discount:
        query_conditions &= Q(orderdetails__product__discount__lte=max_discount)
    if min_current_price:
        query_conditions &= Q(orderdetails__product__current_price__gte=min_current_price)
    if max_current_price:
        query_conditions &= Q(orderdetails__product__current_price__lte=max_current_price)
    if order_status:
        query_conditions &= Q(status=order_status)
    if min_order_total_price:
        query_conditions &= Q(total_price__gte=min_order_total_price)
    if max_order_total_price:
        query_conditions &= Q(total_price__lte=max_order_total_price)
    if order_address:
        query_conditions &= Q(order_address__icontains=order_address)
    if min_paid_time:
        query_conditions &= Q(paid_time__gte=min_paid_time)
    if max_paid_time:
        query_conditions &= Q(paid_time__lte=max_paid_time)
    if min_created_time:
        query_conditions &= Q(o_time__gte=min_created_time)
    if max_created_time:
        query_conditions &= Q(o_time__lte=max_created_time)
    if user_name:
        query_conditions &= Q(user__u_name__icontains=user_name)
    if user_phone:
        query_conditions &= Q(user__u_phone__icontains=user_phone)
    if user_sex:
        query_conditions &= Q(user__u_sex=user_sex)
    if user_email:
        query_conditions &= Q(user__email__icontains=user_email)
    # 应用查询条件
    orders = Orders.objects.filter(query_conditions).distinct() if query_conditions else Orders.objects.none()

    # 分页
    paginator = Paginator(orders, 10)  # 例如每页显示10条记录
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    # 创建一个字典来存储每种状态的订单数量
    status_counts = {status_count['status']: status_count['count'] for status_count in order_status_counts}

    # 将搜索字段回传到模板中，以便保持搜索条件
    context = {
        'orders': paged_orders,
        'product_name': product_name,
        'category_id': category_id,
        'brand': brand,
        'description': description,
        'status': status,
        'audit_status': audit_status,
        'max_stock': max_stock,
        'min_stock': min_stock,
        'min_original_price': min_original_price,
        'max_original_price': max_original_price,
        'min_discount': min_discount,
        'max_discount': max_discount,
        'min_current_price': min_current_price,
        'max_current_price': max_current_price,
        'order_status': order_status,
        'min_order_total_price': min_order_total_price,
        'max_order_total_price': max_order_total_price,
        'order_address': order_address,
        'min_paid_time': min_paid_time,
        'max_paid_time': max_paid_time,
        'min_created_time': min_created_time,
        'max_created_time': max_created_time,
        'user_name': user_name,
        'user_phone': user_phone,
        'user_email': user_email,
        'user_sex': user_sex,
        'order_status_counts': status_counts,
        'query': None
    }

    return render(request, 'shop_order.html', context)


def user_detail(request, user_id):
    user = get_object_or_404(Users, pk=user_id)
    data = {
        'u_name': user.u_name,
        'u_sex': user.u_sex,
        'u_address': user.address,
        'u_email': user.email,
        'u_phone': user.u_phone,
    }
    return JsonResponse(data)


def product_detail(request, p_id):
    # 根据 p_id 获取 ShopProducts 实例
    shop_product = get_object_or_404(ShopProducts, pk=p_id)
    # 从相关联的 Products 实例中获取产品信息
    product = shop_product.product
    data = {
        'p_name': product.p_name,
        'p_type': product.p_type.category_name,  # 假设 ProductCategories 有一个 'category_name' 字段
        'brand': product.brand,
        'current_price': shop_product.current_price,
        'product_desc': shop_product.product_desc,
        'product_status': shop_product.product_status,
        'stock_quantity': shop_product.stock_quantity,
        'original_price': shop_product.original_price,
        'discount': shop_product.discount,
        'product_image_url': shop_product.product_image_url,
        'query': None
    }

    # 返回 JSON 形式的响应
    return JsonResponse(data)


def return_product(request, o_id):
    if request.method == 'POST':
        try:
            # 在数据库中查找订单实例
            order = Orders.objects.get(o_id=o_id)
            # 检查订单状态是否为"待发货"
            if order.status == '待退货':
                # 修改订单状态为"待收货"
                order.status = '已退货'
                # 保存更改
                order.save()
                # 返回一个成功的响应
                return JsonResponse({'success': True, 'new_status': '待收货'})
            else:
                # 如果订单状态不允许发货，则返回一个错误响应
                return JsonResponse({'success': False, 'error': 'Invalid order status for shipment'})
        except Orders.DoesNotExist:
            # 订单不存在时的错误响应
            return JsonResponse({'success': False, 'error': 'Order does not exist'})
        except Exception as e:
            # 捕获其它异常，返回一个错误信息
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        # 对于非POST请求，返回一个错误响应
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def ship_product(request, o_id):
    if request.method == 'POST':
        try:
            # 在数据库中查找订单实例
            order = Orders.objects.get(o_id=o_id)
            # 检查订单状态是否为"待发货"
            if order.status == '待发货':
                # 修改订单状态为"待收货"
                order.status = '待收货'
                # 保存更改
                order.save()
                # 返回一个成功的响应
                return JsonResponse({'success': True, 'new_status': '待收货'})
            else:
                # 如果订单状态不允许发货，则返回一个错误响应
                return JsonResponse({'success': False, 'error': 'Invalid order status for shipment'})
        except Orders.DoesNotExist:
            # 订单不存在时的错误响应
            return JsonResponse({'success': False, 'error': 'Order does not exist'})
        except Exception as e:
            # 捕获其它异常，返回一个错误信息
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        # 对于非POST请求，返回一个错误响应
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def rfm_analysis(request):
    engine = create_engine('mysql+pymysql://web:dzh20030112@47.93.125.169/web')
    products_data = pd.read_sql_query('select * from products', engine)
    orders_data = pd.read_sql_query("select * from orders", engine)
    order_details_data = pd.read_sql_query("select * from order_details", engine)

    # 转换时间类型
    orders_data['o_time'] = pd.to_datetime(orders_data['o_time'])
    orders_data['paid_time'] = pd.to_datetime(orders_data['paid_time'])
    # 将表融合
    merged_data = pd.merge(orders_data, order_details_data, left_on='o_id', right_on='order_id')
    merged_data = pd.merge(merged_data, products_data, left_on='product_id', right_on='p_id')

    merged_data.head(1)

    # 筛选出一年之内的购买记录
    current_time = pd.Timestamp.now()
    two_years_ago = current_time - relativedelta(years=1)
    filtered_data = merged_data[(merged_data['paid_time'] >= two_years_ago) &
                                (merged_data['paid_time'] <= current_time)]

    shop_id = request.session.get('s_id')
    filtered_data = filtered_data.query(f'shop_id == {shop_id}')
    filtered_data.head(1)

    # 创建一个空的DataFrame来存储RFM值
    RFM = pd.DataFrame()
    # 计算R（最近一次购买时间）注意，这个R是dataframe格式
    R = filtered_data.groupby('user_id')['paid_time'].max().reset_index()
    R.columns = ['u_id', 'last_purchase_time']  # 重命名列以避免混淆
    RFM['u_id'] = R['u_id']
    RFM['Recency'] = (pd.Timestamp.now() - R['last_purchase_time']).dt.days
    # 计算F（购买频次）
    F = filtered_data.groupby('user_id').size().reset_index(name='frequency')
    # 使用size()来计算每个组的行数,即该u_id在这一段时间内共出现了多少次。
    RFM['Frequency'] = F['frequency']
    # 计算M（总消费金额）
    M = filtered_data.groupby('user_id')['total_price'].sum().reset_index()
    RFM['Monetary'] = M['total_price']

    R_threshold = RFM['Recency'].mean()
    F_threshold = RFM['Frequency'].mean()
    M_threshold = RFM['Monetary'].mean()
    print(R_threshold)
    print(F_threshold)
    print(M_threshold)

    # 标识高于(1)或低于(0)平均值
    RFM['R'] = (RFM['Recency'] < R_threshold).astype(int)
    RFM['F'] = (RFM['Frequency'] > F_threshold).astype(int)
    RFM['M'] = (RFM['Monetary'] > M_threshold).astype(int)

    RFM['RFM_Class'] = RFM['R'].astype(str) + RFM['F'].astype(str) + RFM['M'].astype(str)

    # 创建中文标签映射
    rfm_labels = {
        '111': '重要价值客户',
        '110': '潜力客户',
        '101': '重要深耕客户',
        '100': '新客户',
        '011': '重要唤回客户',
        '010': '一般维持用户',
        '001': '重要挽留客户',
        '000': '流失用户'
    }

    RFM['RFM_Label'] = RFM['RFM_Class'].map(rfm_labels)

    RFM_data = RFM[['u_id', 'Recency', 'Frequency', 'Monetary', 'RFM_Class', 'RFM_Label']].to_dict(orient='records')

    # 创建一个字典，其中包含您想要在模板中使用的数据
    context = {
        'RFM_data': RFM_data,
        # 如果您还有其他数据需要传递，可以在这里添加
    }

    # 渲染模板，并将上下文传递给模板
    return render(request, 'rfm.html', context)
