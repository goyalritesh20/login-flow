from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'dob',  'bio',]


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False)


# class UserSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     username = serializers.CharField(required=True, allow_blank=False, max_length=100)
#     email = serializers.CharField(required=True, allow_blank=False, max_length=100)
#     first_name = serializers.CharField(required=True, allow_blank=False, max_length=100)
#     last_name = serializers.CharField(required=False, allow_blank=True, max_length=100)
#     bio = serializers.CharField(style={'base_template': 'textarea.html'})
#     gender = serializers.ChoiceField(choices=User.GENDER_CHOICES)
#     dob = serializers.DateField(required=True)

#     def create(self, validated_data):
#         """
#     Create and return a new `Snippet` instance, given the validated data.
#     """
#         print(validated_data)
#         return User.objects.create(**validated_data)