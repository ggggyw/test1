from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
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
                    return redirect(reverse('userpage', kwargs={'ID': user.u_id, 'role': role}))
                else:
                    messages.error(request, 'Invalid username or password.')
            elif role == 'admin':
                try:
                    admin = Admin.objects.get(ad_acc=user_acc)
                    if admin.ad_psw == password:
                        request.session['u_id'] = admin.ad_id
                        request.session['role'] = role
                        return redirect(reverse('userpage', kwargs={'ID': admin.ad_id, 'role': role}))
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
                        return redirect(reverse('userpage', kwargs={'ID': shop.s_id, 'role': role}))
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
        password = request.POST['code']
        role = request.POST['role']

        # Check if this username already exists.
        if Users.objects.filter(name=username).exists():
            return render(request, 'registration.html', {'error': '用户名已经存在'})

        # If not exists, create the user.
        Users.objects.create(name=username, code=password, role=role)
        return redirect('/login/')

    return render(request, 'registration.html')

