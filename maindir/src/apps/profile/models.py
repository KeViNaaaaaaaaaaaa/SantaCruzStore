from django.utils import timezone
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pizda')
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)