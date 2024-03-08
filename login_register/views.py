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
                if (user.u_acc == username) & (user.u_psw == password):
                    return redirect('userspage')
                else:
                    return render(request, 'login.html', {'error': 'Invalid username, password, or role'})
            elif role == 'admin':
                try:
                    user = Admin.objects.get(ad_acc=username)
                    print(user)
                    if (user.ad_acc == username) & (user.ad_psw == password):
                        return redirect('userspage')
                    else:
                        return render(request, 'login.html', {'error': 'Invalid username, password, or role'})
                except Admin.DoesNotExist:
                    return render(request, 'login.html', {'error': 'User not found'})
            elif role == 'merchant':
                try:
                    user = Merchant.objects.get(m_acc=username)
                    print(user)
                    if (user.m_acc == username) & (user.m_psw == password):
                        return redirect('userspage')
                    else:
                        return render(request, 'login.html', {'error': 'Invalid username, password, or role'})
                except Merchant.DoesNotExist:
                    return render(request, 'login.html', {'error': 'User not found'})
            else:
                user = None
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

