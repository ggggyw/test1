from django.shortcuts import render


# Create your views here.
def userspage(request):
    return render(request, 'userpage.html')

def userprofile(request):
    return render(request, 'userprofile.html')

def usercart(request):
    return render(request,'usercart.html')