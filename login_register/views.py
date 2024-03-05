from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from .models import User
from .models import Admin
from .models import Merchant
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST['name']
        password = request.POST['password']
        role = request.POST['role']

        try:
            # 根据角色获取对应的用户模型对象
            if role == 'user':
                user = User.objects.get(u_acc=username)
                print(user)
            elif role == 'admin':
                user = Admin.objects.get(username=username)
            elif role == 'merchant':
                user = Merchant.objects.get(username=username)
            else:
                user = None

            # 如果找到了用户并且密码匹配，进行登录
            if (user.u_acc==username)&(user.u_psw==password):
                print('pipe')
                # 执行登录逻辑
               # request.session['user_id'] = user.id
                #request.session['role'] = role
                return redirect('userspage')
            else:
                return render(request, 'login.html', {'error': 'Invalid username, password, or role'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'User not found'})

    # GET 请求直接渲染登录页面
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['name']
        password = request.POST['code']
        role = request.POST['role']

        # Check if this username already exists.
        if User.objects.filter(name=username).exists():
            return render(request, 'registration.html', {'error': '用户名已经存在'})

        # If not exists, create the user.
        User.objects.create(name=username, code=password, role=role)
        return redirect('/login/')

    return render(request, 'registration.html')

def home(request):
    return render(request, '首页.html')
def userspage(request):
    return render(request, 'userspage.html')