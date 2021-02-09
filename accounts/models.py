import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

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
        seconds = 120
        return (timezone.now() - self.created_on).seconds > seconds

    @classmethod
    def get_reset_token(cls, user):
        obj, created = cls.objects.get_or_create(user=user,defaults={'unique_key': uuid.uuid4().hex},)
        if obj.is_expired():
            obj.delete()
            return cls.get_reset_token(user)
        return (obj, created)

    def __str__(self):
        return '{}'.format(self.user.username)

class UserDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_devices')
    device_ip = models.CharField(max_length=50)
    device_type = models.CharField(max_length=50)
    additional_info = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}-{}'.format(self.device_ip,self.device_type)

@receiver(post_save, sender=UserDevice)
def _post_save_userdevice_receiver(sender, instance, created, **kwargs):
    from accounts.tasks import send_mail_for_user_login
    if created:
        send_mail_for_user_login(instance)