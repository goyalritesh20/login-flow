from django.contrib import admin
from django.urls import path, include
from accounts import views


urlpatterns = [
    path('',views.home_view,name='home-view'),
    path('accounts/login/',views.user_login,name='user-login'),
    path('accounts/logout/',views.logout_view,name='logout-view')

]
