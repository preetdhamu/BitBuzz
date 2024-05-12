from django.db import models
from Listeners.models import l_profile
# Create your models here.

class a_profile(models.Model):
    email=models.CharField(primary_key=True,max_length=255)
    phone_number=models.CharField(max_length=15 , default=False,blank=True)
    name=models.CharField(max_length=100,blank=True)
    user_profile_image=models.ImageField(upload_to="profile",default="defaultprofile.jpg")
    email_token=models.CharField(max_length=200,default=True)
    is_email_verified=models.BooleanField(default=False)
    instaid=models.CharField(max_length=100,blank=True)
    ytname=models.CharField(max_length=150,blank=True)
    follower=models.ManyToManyField(l_profile,related_name='followers')
    bio = models.TextField(default='')
    def __str__(self):
        return f"{self.email} {self.is_email_verified}"


class Song(models.Model):
    songname=models.CharField(max_length=200,unique=True)
    singeremail=models.CharField(max_length=100,blank=True)
    singername=models.CharField(max_length=100,blank=True)
    tags=models.CharField(max_length=100)
    cover=models.ImageField(upload_to='images')
    songfile=models.FileField(upload_to='songs')
    likes=models.ManyToManyField(l_profile,related_name='Liked_Songs')
    def __str__(self):
        return f"{self.songname} {self.singername} {self.singeremail}"