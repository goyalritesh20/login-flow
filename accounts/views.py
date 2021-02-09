from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
import uuid, random
from accounts.models import ForgotPassword, UserDevice
from django.contrib.auth import get_user_model
User = get_user_model()
from django.urls import reverse
from accounts.forms import UserForm
from accounts.tasks import send_mail_new_user_register, send_mail_for_reset_password, send_mail_for_user_login
from django.utils import timezone

# Create your views here.
def fetch_user_agent_info(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if request.user_agent.is_mobile:
        device_type = "Mobile"
    elif request.user_agent.is_tablet:
        device_type = "Tablet"
    elif request.user_agent.is_pc:
        device_type = "PC"
    else:
        device_type = 'Unknown'

    user_agent_info = {
        "ip": ip,
        "device_type": device_type,
        "browser_type": request.user_agent.browser.family,
        "browser_version": request.user_agent.browser.version_string,
        "os_type": request.user_agent.os.family,
        "os_version": request.user_agent.os.version_string,
        "access_at": timezone.now().strftime("%B %d, %Y %H:%M:%S %Z(%z)")
    }
    return user_agent_info


@login_required
def home_view(request):
    context = fetch_user_agent_info(request)

    return render(request,'home.html', context)


def user_login(request):
    template_name = 'userlogin.html'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                user_agent_info = fetch_user_agent_info(request)
                additional_info = "{} {} {} from {} {}".format(user_agent_info['device_type'],user_agent_info['os_type'],user_agent_info['os_version'],user_agent_info['browser_type'],user_agent_info['browser_version'],)
                obj, created = UserDevice.objects.get_or_create(
                    user=request.user,
                    device_ip=user_agent_info['ip'],
                    device_type=user_agent_info['device_type'],
                    defaults={'additional_info':additional_info}
                    )
                print(obj.id, created, obj)
                # send_mail_for_user_login(user, user_agent_info)

                return redirect('/')
            else:
                ctx = {'error':'Incorrect username and password'}
                return render(request, template_name, ctx)
        else:
            ctx = {'error':'Invalid username and password'}
            return render(request, template_name, ctx)

    return render(request, template_name)


def logout_view(request):
    logout(request)
    return redirect('/')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email and User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            obj, created = ForgotPassword.get_reset_token(user=user)

            if request.GET.get('otp'):
                if not obj.otp:
                    obj.otp = random.randint(123456,987654)
                    obj.save()
                link = reverse('reset-password-otp')
                if not created:
                    ctx = {'message':'Please check your email for otp','link':link}
                else:
                    # send_resetpassword_otp()
                    ctx = {'message':'An OTP has been sent to your email for password reset valid for 30 seconds','link':link}

            else:
                pwd_reset_link = reverse('reset-password', kwargs={'key':obj.unique_key})
                send_mail_for_reset_password(user, pwd_reset_link)
                if not created:
                    ctx = {'message':'Please check your email for password reset link'}
                else:
                    # send_resetpassword_link()
                    ctx = {'message':'A link has been sent to your email for password reset'}
            return render(request,'forgotpassword.html',ctx)

        else:
            ctx = {'error':'Invalid email address'}
            return render(request,'forgotpassword.html',ctx)
    else:
        return render(request,'forgotpassword.html')


def reset_password(request,key):
    template_name = 'resetpassword.html'
    ctx = {}
    obj = ForgotPassword.objects.filter(unique_key=key).first()

    if not obj:
        ctx = {'error':'Invalid Link or Link Expired','invalid':True}
        return render(request, template_name, ctx)

    if obj.is_expired():
        obj.delete()
        ctx = {'error':'Link has been expired','invalid':True}
        return render(request, template_name, ctx)

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')

        if not password or not confirm_password:
            ctx = {'error':'Please enter both Password and confirm password'}
            return render(request, template_name, ctx)

        elif password != confirm_password:
            ctx = {'error':'Password and confirm password should be same'}
            return render(request, template_name, ctx)

        else:
            user = obj.user
            user.set_password(password)
            user.save()
            obj.delete()
            return render(request, 'resetdone.html', ctx)

    return render(request, template_name, ctx)


def reset_password_otp(request):

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')
        otp = request.POST.get('otp')

        if not otp.isnumeric():
            ctx = {'error':'Invalid OTP','invalid':True}
            return render(request, 'resetpasswordotp.html',ctx)

        obj = ForgotPassword.objects.filter(otp=otp).first()

        if not obj:
            ctx = {'error':'Invalid OTP or OTP Expired','invalid':True}
            return render(request, 'resetpasswordotp.html',ctx)

        if obj.is_expired():
            obj.delete()
            ctx = {'error':" OTP expired",'invalid':True}
            return render(request,'resetpasswordotp.html',ctx)

        if not (password and confirm_password and otp):
            ctx = {'error':'Please enter all the mandatory information'}
            return render(request,'resetpasswordotp.html',ctx)

        elif password != confirm_password:
            ctx = {'error':'Password and confirm password should be same'}
            return render(request,'resetpasswordotp.html',ctx)

        else:
            user = obj.user
            user.set_password(password)
            user.save()
            obj.delete()
            return render(request,'resetdone.html')

    return render(request,'resetpasswordotp.html')


def register(request):
    ctx = {}
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user_obj = form.save()
            obj, created = ForgotPassword.get_reset_token(user=user_obj)

            pwd_reset_link = reverse('reset-password', kwargs={'key':obj.unique_key})
            send_mail_new_user_register(user_obj, pwd_reset_link)

            return redirect('/')

    else:
        form = UserForm()

    ctx['form'] = form
    return render(request,'register.html', ctx)