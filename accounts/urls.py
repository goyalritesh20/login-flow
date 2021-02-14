from django.contrib import admin
from django.urls import path, include
from accounts import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('',views.home_view,name='home-view'),
    path('accounts/login/',views.user_login,name='user-login'),
    path('accounts/logout/',views.logout_view,name='logout-view'),
    path('forgotpassword/',views.forgot_password,name='forgot-password'),

    path('resetpassword/otp/', views.reset_password_otp, name='reset-password-otp'),
    path('resetpassword/<str:key>/',views.reset_password,name='reset-password'),

    path('register/', views.register, name='register'),
]

urlpatterns += [

    path('api/users/', views.user_list_api, name='user-list-api'),
    path('api/user/<int:pk>/', views.user_detail_api, name='user-detail-api'),
    path('class-api/users/', views.UserListAPI.as_view()),
    path('class-api/user/<int:pk>/', views.UserDetailAPI.as_view()),
    path('api/login/',views.UserLoginAPI.as_view(),name='user-login-api'),
]


urlpatterns = format_suffix_patterns(urlpatterns)


# from django.urls import path, include
# from django.contrib.auth import get_user_model
# User = get_user_model()
# from rest_framework import routers, serializers, viewsets

# # Serializers define the API representation.
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ['url', 'username', 'email', 'is_staff']

# # ViewSets define the view behavior.
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# # Routers provide an easy way of automatically determining the URL conf.
# router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)

# # Wire up our API using automatic URL routing.
# # Additionally, we include login URLs for the browsable API.
# urlpatterns = [
#     path('', include(router.urls)),
#     path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# ]
