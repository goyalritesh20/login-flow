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


from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from accounts.serializers import UserSerializer, UserLoginSerializer, ForgotPasswordSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes

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


@api_view(['GET','POST'])
def user_list_api(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        # return JsonResponse(serializer.data, safe=False)
        return Response(serializer.data)

    elif request.method == 'POST':
        # data = JSONParser().parse(request)
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def user_detail_api(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        user_obj = User.objects.get(pk=pk)
    except User.DoesNotExist:
        response = {'msg':'No Record Found'}
        return Response(response, status=404)

    if request.method == 'GET':
        serializer = UserSerializer(user_obj)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # data = JSONParser().parse(request)
        data = request.data
        serializer = UserSerializer(user_obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        response = {'msg':'{} Record Deleted successfully'.format(user_obj.username)}
        user_obj.delete()
        return Response(response, status=204)


class UserListAPI(APIView):
    """
    List all users, or create a new snippet.
    """
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPI(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user_obj = self.get_object(pk)
        serializer = UserSerializer(user_obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user_obj = self.get_object(pk)
        serializer = UserSerializer(user_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user_obj = self.get_object(pk)
        user_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserLoginAPI(APIView):

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username= serializer.data.get('username')
            password = serializer.data.get('password')
            if username and password:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    detail = {'detail':'Valid Credentials'}
                    return Response(detail, status=status.HTTP_201_CREATED)

            detail = {'detail':'Please enter valid Username and Password'}
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordAPT(APIView):
    def post(self, request, format=None):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email')
            if email and User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                obj, created = ForgotPassword.get_reset_token(user=user)

                pwd_reset_link = reverse('reset-password', kwargs={'key':obj.unique_key})
                send_mail_for_reset_password(user, pwd_reset_link)
                if not created:
                    response = {'detail':'Please check your email for password reset link'}
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    response = {'message':'A link has been sent to your email for password reset'}
                    return Response(response, status=status.HTTP_201_CREATED)

            response = {'message':'Please enter valid email address'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)