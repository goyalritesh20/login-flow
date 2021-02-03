from django.contrib import admin
from django.urls import path, include
from accounts import views


urlpatterns = [
    path('',views.home_view,name='home-view'),
    path('accounts/login/',views.user_login,name='user-login'),
    path('accounts/logout/',views.logout_view,name='logout-view'),
    path('forgotpassword/',views.forgot_password,name='forgot-password'),

    path('resetpassword/otp/', views.reset_password_otp, name='reset-password-otp'),
    path('resetpassword/<str:key>/',views.reset_password,name='reset-password'),

    path('register/', views.register, name='register'),
]
