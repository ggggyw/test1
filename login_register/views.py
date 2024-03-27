from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from common.models import Users
from common.models import Admin
from common.models import Shops

def login(request):
    if request.method == 'POST':
        user_acc = request.POST['name']
        password = request.POST['password']
        role = request.POST['role']

        try:
            if role == 'user':
                user = Users.objects.get(u_acc=user_acc)
                if user.u_psw == password:
                    request.session['u_id'] = user.u_id  # 将用户ID存入session
                    request.session['role'] = role  # 将角色存入session
                    return redirect(reverse('userpage'))  # 重定向到用户页面
                else:
                    messages.error(request, 'Invalid username or password.')
            elif role == 'admin':
                try:
                    admin = Admin.objects.get(ad_acc=user_acc)
                    if admin.ad_psw == password:
                        request.session['u_id'] = admin.ad_id
                        request.session['role'] = role
                        return redirect(reverse('userpage'))
                    else:
                        messages.error(request, 'Invalid username or password.')
                except Admin.DoesNotExist:
                    messages.error(request, 'Admin not found.')
            elif role == 'shop':
                try:
                    shop = Shops.objects.get(s_acc=user_acc)
                    if shop.s_psw == password:
                        request.session['u_id'] = shop.s_id
                        request.session['role'] = role
                        return redirect(reverse('userpage'))
                    else:
                        messages.error(request, 'Invalid username or password.')
                except Shops.DoesNotExist:
                    messages.error(request, 'Shop not found.')
            else:
                messages.error(request, 'Invalid role.')
        except Users.DoesNotExist:
            messages.error(request, 'User not found.')

    # 对于GET请求，或者是身份验证失败的情况，渲染登录页面
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['name']
        password = request.POST['password']
        role = request.POST['role']

        if role == 'user':
            if Users.objects.filter(u_acc=username).exists():
                messages.error(request, '该用户已经存在！')
            else:
                # 创建用户时加入 created_at 字段的值
                Users.objects.create(
                    u_acc=username,
                    u_psw=password,
                    created_at=timezone.now()  # 使用 Django 的 timezone.now() 设置当前时间
                )
                messages.success(request, '用户注册成功！快去登录吧！')
                return redirect('/user/login/')

        elif role == 'shop':
            if Shops.objects.filter(s_acc=username).exists():
                messages.error(request, '该商家已经存在！')
            else:
                Shops.objects.create(s_acc=username, s_psw=password)
                messages.success(request, '商家注册成功！快去登录吧！')
                return redirect('/user/login/')

        else:
            messages.error(request, '选择了无效的角色')

    # 显示register.html页面
    return render(request, 'registration.html')

