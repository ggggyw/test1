from django.shortcuts import render, redirect
from .models import User
from django.http import HttpResponse
# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST['name']  # 注意字段名称
        password = request.POST['password']
        role = request.POST['role']

        try:
            user = User.objects.get(name=username)

            # Validate password
            if user.password == password and user.role == role:
                # Password is correct, login the user
                request.session['username'] = username
                request.session['role'] = role

                return redirect('/home/')  # Redirects to home view
            else:
                # Password incorrect or role not correct, return to login
                return render(request, 'login.html', {'error': '密码错误或者角色不对'})

        except User.DoesNotExist:
            # Username does not exist in the database
            return render(request, 'login.html', {'error': '用户名不存在'})

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