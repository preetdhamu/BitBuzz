import uuid
import random
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import logout,authenticate,login as mylogin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth import get_user_model
from .utils import *
from Artists.models import a_profile
from Listeners.models import l_profile
from django.contrib.auth.hashers import check_password
from social_django.models import UserSocialAuth
from django.views import View
User=get_user_model()
# Create your views here.


def login(request):
      if request.method=='POST':
        try:
            email=request.POST.get('email')
            password=request.POST.get('password')
        
            user_object=User.objects.filter(email=email,is_artists=True).first()
        

            if user_object is None:
                messages.success(request,'Username Not Found , Register First')
                return redirect('/accounts')
            else:
                obj=a_profile.objects.filter(email=email).first()
            
                if not obj.is_email_verified:
                    messages.success(request,'Email is Not Verified Yet')
                    return redirect('/accounts')

                


                # Authentication with email and password 
                user=authenticate(email=email,password=password) 
                if user is None:
                    messages.success(request,'Wrong Password')
                    return redirect('/accounts')  
                else:    
                    mylogin(request,user)
                    
                
                    return redirect('/accounts/Artists')
        except Exception as e:
            print(e)            
      return render(request,'signin.html')


class ContinueWithGoogleView(View):
    def get(self, request):
        try:
            email=UserSocialAuth.objects.latest('id').uid
    
            if not a_profile.objects.filter(email=email).first():
                auth_token=str(uuid.uuid4())
                new_profile=a_profile.objects.create(email=email,email_token=auth_token) 
                new_profile.is_email_verified=True
                new_profile.save()

        except Exception as e:
            print(e)
        return redirect('/accounts/Artists')


def register(request): 
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        phone_number=request.POST.get('phone_number')
        try:
            if User.objects.filter(email=email,is_artists=True).first():
                messages.success(request,'Email is Already Taken')
                return redirect('/accounts/register')
            if a_profile.objects.filter(phone_number=phone_number).first():
                messages.success(request,'Phone Number is Already Taken')
                return redirect('/accounts/register')
            user_obj=User.objects.create(email=email,phone_number=phone_number,is_artists=True)  
            user_obj.set_password(password) 
            user_obj.save()
            auth_token=str(uuid.uuid4())
            new_profile=a_profile.objects.create(email=email,phone_number=phone_number,email_token=auth_token) 
            new_profile.save()
            send_email_token(email,auth_token,'Artists')
            messages.success(request, 'Please Check your Email')
            print('Please Check your Email')
            return redirect('/accounts/')
        except Exception as e:
            print(e)
    return render(request,'signup.html')    




def logout_view(request):
    logout(request)
    return redirect("logout")


def verify(request,token,value):  
    try:
        if value=='Artists':
            a=a_profile.objects.get(email_token=token) 
            a.is_email_verified=True
            a.save()
            return HttpResponse('Your Account is Verified')
        if value=='Listener':    
            a=l_profile.objects.get(email_token=token) 
            a.is_email_verified=True
            a.save()
            return HttpResponse('Your Account is Verified')
    except Exception as e:
        print(e)
        return HttpResponse('Error Occured due to Invalid token')    








def forget(request):
    if request.method=='POST':
        email=request.POST.get('email')
        user_object=User.objects.filter(email=email,is_artists=True).first()
        
        if user_object is None:
            messages.success(request,'Username Not Found')
            return redirect('/accounts')
        else:
        # profile_obj=Profile.objects.filter(user=user_object).first()
            otp=random.randrange(9999,999999)
            # l.append(otp)
            # otp=9652
            # l.append(email)
            send_email_otp(email,otp)
            messages.success(request,"Please Enter a OTP ")
            return render(request,'forget_otp.html',{'email':email,'otp_back':otp})
            # return redirect(f"/verify_pass_code/{email}/{otp}")


    return render(request,'forget.html')



def verify_pass_code(request,email,otp):
    if request.method=='POST':
        otp1=request.POST.get('otp1')
        print(type(otp),type(otp1))
        print(otp,otp1)
        if(otp==int(otp1)):
            return redirect(f'/accounts/new_pass/{email}')
            # return render(request,'new_pass.html',{'email':email})
        else:
            messages.warning(request,'Enter Correct Otp,Try Again')
            return redirect('/accounts')
    return HttpResponse('Good')

def forget_otp(request):
    pass


def new_pass(request,email):
    try:
        if request.method=='POST':
            password1=request.POST.get('password1')
            password2=request.POST.get('password2')
            
            print(email,password1,password2)
            user_object=User.objects.filter(email=email ,is_artists=True).first()
            
            if password1!=password2:
                messages.success(request,'Password not Match')
                return redirect(f'/new_pass/{email}')
            user_object=User.objects.get(email=email,is_artists=True)
            user_object.set_password(password1)
            user_object.save()
            messages.warning(request,'Password Reseted')
            return redirect('/accounts')
    except Exception as e:
        print(e)
    return render(request,'new_pass.html')


