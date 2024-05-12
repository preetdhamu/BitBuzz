from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from datetime import datetime,timedelta
User=get_user_model()
# Create your views here.
@login_required
def Artists(request):
        try:
            photo=a_profile.objects.filter(email=request.user.email).first() 
            song=Song.objects.filter(singeremail=request.user.email)
        except Exception as e:
            print(e)
            messages.success(request,'No Song Found')
        return render(request,'index.html',{'song':song,'photo':photo})


def edit(request):
    if request.method=='POST':
        a_profile_email=request.POST.get('email')
        a_profile_phone=request.POST.get('phone')
        a_profile_bio=request.POST.get('bio')
        a_profile_image=request.FILES.get('image')
        print(a_profile_email,a_profile_phone,a_profile_bio,a_profile_image)   
        try:
            queryset=a_profile.objects.filter(email=a_profile_email).first()
            queryset.email=a_profile_email
            queryset.phone_number =a_profile_phone
            queryset.bio=a_profile_bio
            if a_profile_image:
                queryset.user_profile_image=a_profile_image
            queryset.save()
            success='Profile Updated successfully'
            return HttpResponse(success)
        except Exception as e:
            print(e)

def songedit(request):
    if request.method=='POST':
        songid=request.POST.get('songid')
        songname=request.POST.get('songname')
        singername=request.POST.get('singername')
        tags=request.POST.get('tags')
        cover=request.FILES.get('cover')
        print(songid,songname,singername,tags,cover)
        
            
        try:
            queryset=Song.objects.filter(id=songid).first()
            queryset.songname=songname
            queryset.singername=singername
            queryset.tags=tags
            
            if cover:
                queryset.cover=cover
            queryset.save()
            success='Song Updated successfully'
            return HttpResponse(success)
        except Exception as e :
            print(e)
        return render(request,'index.html') 





def deletesong(request, id):
    # <built-in function id>
    try:
        songs = Song.objects.filter(id=id)
        songs.delete()
        return redirect("/accounts/Artists/")
    except Exception as e:
        print(e)    
    return render(request,"index.html")   




def Music(request):
    if request.method=='POST':
        
        songname=request.POST.get('songname')
        singeremail=request.POST.get('singeremail')
        singername=request.POST.get('singername')
        tags=request.POST.get('tags')
        cover = request.FILES.get('cover')
        songfile = request.FILES.get('songfile')
        try:
            if Song.objects.filter(songname=songname).first():
                messages.success(request,'Song Name is Already Taken')
                return redirect('/accounts/Artists/Music')

            if a_profile.objects.filter(email=singeremail).first():   
                song=Song(singeremail=singeremail,songname=songname,singername=singername,tags=tags,cover=cover,songfile=songfile)   
                song.save()
                messages.success(request,'Song is Uploaded to BitBuzz')
                return redirect('/accounts/Artists')
            else:
                messages.success(request,'U are not authorisez person')
                redirect('/logout')
                   
        except Exception as e:
            print(e)
    return render(request,'music.html')




def follower_data_api(request):
    timestamps = [datetime.now() - timedelta(minutes=i) for i in range(5)]
    minutes = [int(ts.strftime('%M')) for ts in timestamps]
    
    print(request.user.email)
    profile = a_profile.objects.filter(email=request.user.email).first()
    follower_counts = [profile.follower.count() for _ in range(5)]
    song = Song.objects.filter(email=request.user.email).first()
    likes = [song.likes.count() for _ in range(5)]
    print(minutes)
    print(follower_counts)
    
    # Calculate the change in followers
    follower_changes = [follower_counts[i] - follower_counts[i - 1] for i in range(1, len(follower_counts))]
    
    data = {
        'minute': minutes[1:],  # Exclude the first timestamp for change calculation
        'follower_change': follower_changes,
        'likes':likes,
    }
    return JsonResponse(data)
