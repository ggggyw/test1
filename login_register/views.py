from django.shortcuts import render, redirect
from django.urls import reverse

from common.models import Users
from common.models import Admin
from common.models import Shops

def login(request):
    if request.method == 'POST':
        user_acc = request.POST['name']
        password = request.POST['password']
        role = request.POST['role']

        try:
            # 根据角色获取对应的用户模型对象
            if role == 'user':
                user = Users.objects.get(u_acc=user_acc)
                if (user.u_acc == user_acc) & (user.u_psw == password):
                    user_id = user.u_id  # 获取用户ID
                    return redirect(reverse('userpage', kwargs={'ID': user_id, 'role': role}))  #返回用户ID和角色
                else:
                    return render(request, 'login.html', {'error': 'Invalid username, password, or role'})
            elif role == 'admin':
                try:
                    user = Admin.objects.get(ad_acc=user_acc)
                    print(user)
                    if (user.ad_acc == user_acc) & (user.ad_psw == password):
                        admin_id = user.ad_id  # 获取管理员ID
                        return redirect(reverse('userpage', kwargs={'ID': admin_id, 'role': role}))  # 返回管理员ID和角色
                    else:
                        return render(request, 'login.html', {'error': 'Invalid username, password, or role'})
                except Admin.DoesNotExist:
                    return render(request, 'login.html', {'error': 'User not found'})
            elif role == 'shop':
                try:
                    user = Shops.objects.get(s_acc=user_acc)
                    print(user)
                    if (user.s_acc == user_acc) & (user.s_psw == password):
                        shop_id = user.s_id   #获取商家ID
                        return redirect(reverse('userpage', kwargs={'ID': shop_id, 'role': role}))  # 返回商家ID和角色
                    else:
                        return render(request, 'login.html', {'error': 'Invalid username, password, or role'})
                except Shops.DoesNotExist:
                    return render(request, 'login.html', {'error': 'User not found'})
            else:
                user = None
        except Users.DoesNotExist:
            return render(request, 'login.html', {'error': 'User not found'})

    # GET 请求直接渲染登录页面
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['name']
        password = request.POST['code']
        role = request.POST['role']

        # Check if this username already exists.
        if Users.objects.filter(name=username).exists():
            return render(request, 'registration.html', {'error': '用户名已经存在'})

        # If not exists, create the user.
        Users.objects.create(name=username, code=password, role=role)
        return redirect('/login/')

    return render(request, 'registration.html')

