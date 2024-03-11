from django.shortcuts import render
from login_register.models import Products


# Create your views here.
def userspage(request):
    products = Products.objects.all()  # 获取所有商品对象
    context = {'products': products}  # 构建上下文字典
    return render(request, 'userpage.html',context)

def userprofile(request):
    return render(request, 'userprofile.html')

def usercart(request):
    return render(request,'usercart.html')

def product_details(request, p_id):
    product = Products.objects.get(p_id=p_id)
    return render(request, 'productdetails.html', {'product': product})