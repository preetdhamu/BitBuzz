from django.db import models

# Create your models here.

class l_profile(models.Model):
    name=models.CharField(max_length=50,default=False)
    email=models.CharField(max_length=125,default=False)
    phone_number=models.CharField(max_length=15 , default=False,blank=True)
    email_token=models.CharField(max_length=200,default=True)
    
    is_email_verified=models.BooleanField(default=False)
    dob = models.DateTimeField(null=True)
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    def __str__(self):
        return f"{self.id} {self.name} {self.phone_number} {self.email} {self.dob} {self.gender}"

class otp_grabber(models.Model):
    phone_number=models.CharField(max_length=15 , primary_key=True)
    otp=models.CharField(max_length=20,null=True)

    def __str__(self):
        return f"{self.phone_number} {self.otp}"

