from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class ForgotPassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unique_key = models.CharField(max_length=50)
    otp = models.IntegerField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        seconds = 30
        return (timezone.now() - self.created_on).seconds > seconds

    def __str__(self):
        return '{}'.format(self.user.username)