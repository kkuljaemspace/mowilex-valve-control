from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.urls import reverse


# Create your models here.
class Profile(AbstractUser):
    photo = models.FileField(upload_to='profile_photos/', null=True, blank=True)

    def __str__(self):
        return self.username


class AppIdentity(models.Model):
    nickname = models.CharField(max_length=255, null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    logo = models.FileField(upload_to='logo/', null=True, blank=True)

    def __str__(self):
        return self.nickname


class Menu(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Submenu(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='submenus', null=True, blank=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=200)  # Tambahkan field ini
    groups = models.ManyToManyField(Group, blank=True)

    def __str__(self):
        return self.name