from django.shortcuts import render


# Create your views here.
def userspage(request):
    return render(request, 'userspage.html')
