from django.shortcuts import render, redirect
from django.contrib import messages
from common.models import Admin

def adminpage(request):
    if 'ad_id' not in request.session:
        return redirect('login')

    admin = Admin.objects.get(ad_id=request.session['ad_id'])
    context = {
        'admin': admin,
        'is_super': admin.is_super
    }
    return render(request, 'adminpage.html', context)
