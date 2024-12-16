from django.utils import timezone
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User
from apps.catalog.models import Product


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)

class Promocode(models.Model):
    email = models.EmailField(max_length=30)
    promocode = models.CharField(max_length=8)
    val_of_activate = models.PositiveIntegerField(default=1)

    def __str__(self):
        return 'Promokod for email {}'.format(self.email)