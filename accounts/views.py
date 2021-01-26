from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

# Create your views here.

@login_required
def home_view(request):
    return render(request,'home.html',{})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                ctx = {'error':'Incorrect username and password'}
                return render(request,'userlogin.html',ctx)
        else:
            ctx = {'error':'Invalid username and password'}
            return render(request,'userlogin.html',ctx)
    
    return render(request,'userlogin.html')


def logout_view(request):
    logout(request)
    return redirect('/')