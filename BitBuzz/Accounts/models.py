from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
class CustomUser(AbstractUser):
    username=None
    email=models.CharField(max_length=100, unique=True)
    phone_number=models.CharField(max_length=15 , default=False)
    google_user_id=models.CharField(max_length=10,blank=True)
    is_artists=models.BooleanField(default=False)
    is_listener=models.BooleanField(default=False)
    objects=UserManager() 

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    def __str__(self):
        return f"{self.email} {self.phone_number}"  

