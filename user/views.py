from django.shortcuts import render
from login_register.models import Product


# Create your views here.
def userspage(request):
    products = Product.objects.all()  # 获取所有商品对象
    context = {'products': products}  # 构建上下文字典
    return render(request, 'userpage.html',context)

def userprofile(request):
    return render(request, 'userprofile.html')

def usercart(request):
    return render(request,'usercart.html')
