from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
import uuid
from accounts.models import ForgotPassword
from django.contrib.auth.models import User

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


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email and User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            obj, created = ForgotPassword.objects.get_or_create(user=user,defaults={'unique_key': uuid.uuid4().hex},)
            if not created:
                ctx = {'error':'Please check your email for password reset link'}
                return render(request,'forgotpassword.html',ctx)
            else:
                # send_resetpassword_link() http://localhost:8000/resetpassword/unique_key/
                link = 'http://localhost:8000/resetpassword/{}'.format(obj.unique_key)
                print(link)
                ctx = {'error':'A link has been sent to your email for password reset'}
                return render(request,'forgotpassword.html',ctx)

        else:
            ctx = {'error':'Invalid email address'}
            return render(request,'forgotpassword.html',ctx)
    else:
        return render(request,'forgotpassword.html')


def reset_password(request,key):

    if not ForgotPassword.objects.filter(unique_key=key).exists():
        ctx = {'error':'Invalid Link or Link Expired','invalid':True}
        return render(request,'resetpassword.html',ctx)

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')

        if not password or not confirm_password:
            ctx = {'error':'Please enter both Password and confirm password'}
            return render(request,'resetpassword.html',ctx)

        elif password != confirm_password:
            ctx = {'error':'Password and confirm password should be same'}
            return render(request,'resetpassword.html',ctx)
        
        else:
            obj = ForgotPassword.objects.get(unique_key=key)         
            user = obj.user
            user.set_password(password)
            user.save()
            obj.delete()
            return render(request,'resetdone.html')

    return render(request,'resetpassword.html')