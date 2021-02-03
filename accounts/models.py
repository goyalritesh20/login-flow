from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

# Create your models here.

class User(AbstractUser):
    GENDER_CHOICES = (('M','Male'),('F','Female'))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=50)
    bio = models.TextField(blank=True)
    dob = models.DateField()


class ForgotPassword(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    unique_key = models.CharField(max_length=50)
    otp = models.IntegerField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        seconds = 30
        return (timezone.now() - self.created_on).seconds > seconds

    def __str__(self):
        return '{}'.format(self.user.username)


