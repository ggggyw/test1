from django.http import HttpResponse
from django.shortcuts import render
from login_register.models import Products


def home(request):
    products = Products.objects.all()  # 获取所有商品对象
    context = {'products': products}  # 构建上下文字典
    return render(request, '首页.html',context)
