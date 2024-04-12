from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from .forms import ShopProductForm, ProductForm
from common.models import ShopProducts, ProductCategories, Products, Orders, OrderDetails


# Create your views here.
# 商家页面
def shoppage(request):
    # 从会话中获取用户的ID
    s_id = request.session.get('s_id')
    shop_products = ShopProducts.objects.filter(shop__s_id=s_id)
    paginator = Paginator(shop_products, 3)  # 假设每页显示多少个商品
    products = Products.objects.all()
    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    s_id = request.session.get('u_id')
    role = request.session.get('role')

    context = {
        'shop_products': paged_products,
        'products': products,
        's_id': s_id,
        'role': role
    }
    return render(request, 'shoppage.html', context)


def myproducts(request):
    # 从会话中获取用户的ID
    s_id = request.session.get('s_id')
    # 从GET请求中获取类别ID
    category_id = request.GET.get('category_id')
    if category_id is not None and category_id != '0':
        types = ProductCategories.objects.filter(category_id=category_id).values_list('category_id', flat=True)
        ids = Products.objects.filter(p_type__in=types).values_list('p_id', flat=True)
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id, product_id__in=ids)
    else:
        # 如果没有接收到 category_id 参数，就获取这个u_id商家的全部商品
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id)

    products = Products.objects.all()

    # 创建一个 Paginator 对象，每页显示 24 个商品
    paginator = Paginator(shop_products, 3)
    # 从 GET 请求的查询参数中获取页码
    page = request.GET.get('page')
    # 使用 Paginator 对象的 get_page 方法来获取当前页的商品
    shop_products = paginator.get_page(page)

    # 检查用户是否已经登录
    if 's_id' in request.session:
        # 如果用户已经登录
        template_name = 'shop_my_products.html'
    else:
        # 如果用户没有登录，就渲染 首页.html 模板
        template_name = '首页.html'

    content = render_to_string(template_name,
                               {'shop_products': shop_products, 'products': products, 'category_id': category_id})
    return HttpResponse(content)


def shop_productdetails(request, p_id):
    s_id = request.session.get('s_id')
    role = request.session.get('role')
    shop_product = ShopProducts.objects.get(shop_product_id=p_id)
    products = Products.objects.get(p_id=shop_product.product_id)
    return render(request, 'shop_product_details.html',
                  {'shop_product': shop_product, 'products': products, 's_id': s_id, 'role': role})


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
        'shop_product_form': shop_product_form
    }
    return render(request, 'shop_manage_products.html', context)


def edit_product(request, product_id):
    shop_product = get_object_or_404(ShopProducts, pk=product_id)
    product = shop_product.product

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
        'shop_products': shop_product
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

    # 将订单传递给模板
    context = {
        'orders': orders,
    }
    return render(request, 'shop_order.html', context)

def product_detail(request):
    return None

def sales_analysis(request):
    return render(request, 'shop_sales_analysis.html')

