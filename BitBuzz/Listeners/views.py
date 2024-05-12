from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from .helper import send_otp_to_phone,CustomThread
from .models import l_profile,otp_grabber
from django.contrib.auth import logout,authenticate,login as mylogin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from Accounts.utils import send_email_token
from django.contrib.sessions.backends.db import SessionStore
from django.db.models import Q
from Artists.models import Song,a_profile
from django.utils import timezone
from django.dispatch import Signal
from spellchecker import SpellChecker
import speech_recognition as sr 
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio
import pyttsx3
import uuid
import json
import random
import Levenshtein
import string
import datetime
import pyjokes
import os
import sounddevice as sd
import numpy as np
import pvporcupine
from threading import *
from scipy.io import wavfile
from django.conf import settings


wake_word_detected_signal = Signal()
wake_word_model_path = os.path.join(settings.BASE_DIR, 'Listeners', 'static', 'ram1.ppn')
access_key=settings.ACCESS_KEY
porcupine = pvporcupine.create(keyword_paths=[wake_word_model_path], access_key=access_key)
frame_length = porcupine.frame_length
sample_rate = porcupine.sample_rate
device = None  # Use the default audio input device
chunk_size = frame_length * 10
buffer = np.zeros(chunk_size, dtype=np.int16)
buffer_idx = 0
channel_layer = get_channel_layer()


# Event to signal when to stop the audio processing
stop_event = Event()



wake_word_detected = Event()
background_sound_file = os.path.join(settings.BASE_DIR, 'Listeners', 'static', 'chime.wav')
sample_rate_bg, background_sound = wavfile.read(background_sound_file)




        
def process_audio(samples):
    
    global buffer, buffer_idx,channel_layer
    result = porcupine.process(samples)
    # print('Objects Processed')
    # print(result)
    if result >= 0:
        print("Hey Dimmy detected!")
        sd.play(background_sound, samplerate=sample_rate_bg)
        data=hey_dimmy_command_getter()
             
        print('PreetDhamu')
        print(data)
        if data!='j' or data!='t':
            async_to_sync(channel_layer.group_send)(
            "group_name",  
            {
                'type': 'my_custom_function',
                'data':data,
            }
            )
        else: 
            pass

     
        
def audio_callback(indata, frames, time, status):
    global buffer, buffer_idx
    try:
        if any(indata):
            # Add incoming audio samples to the circular buffer
            buffer[buffer_idx:buffer_idx + len(indata)] = np.int16(indata * 32767).flatten()
            buffer_idx += len(indata)

            # Process audio in chunks of the expected frame length
            while buffer_idx >= frame_length:
                pcm = buffer[:frame_length]
                buffer = np.roll(buffer, -frame_length)
                buffer_idx -= frame_length
                process_audio(pcm)
                


            # Check if the stop event has been set
            if stop_event.is_set():
                raise sd.CallbackStop

    except Exception as e:
        print(e)
# Start the audio stream in a separate thread

def start_audio_stream():
    global listening
    with sd.InputStream(samplerate=sample_rate, device=device, channels=1, callback=audio_callback):
        print("Listening for 'Hey Dimmy'...")
        
        try:
            stop_event.wait()  # Block the main thread until the stop event is set
        except KeyboardInterrupt:
            pass
        finally:
            stop_event.set()  # Set the stop event to terminate the audio processing gracefully







# Start the audio stream in a separate thread
audio_thread = Thread(target=start_audio_stream)
audio_thread.daemon = True
audio_thread.start()

# Add a shutdown hook to stop the audio stream gracefully
import atexit
@atexit.register
def stop_audio_stream():
    print("Stopping audio stream...")
    stop_event.set()  # Set the stop event to signal the audio_thread to stop
    audio_thread.join()
    print("Audio stream stopped.")



User=get_user_model()
# Create your views here.
def homelistener(request):    
            artists=a_profile.objects.all()
            top_songs=Song.objects.all()
            songs_data=[]
            for song in top_songs:
                songs_data.append({
                    'id': song.id,
                    'songName': f'{song.songname}<br><div class="subtitle">{song.singername}</div>',
                    'cover': song.cover.url,
                    'file': song.songfile.url if song.songfile else None
                })
            songs_json=json.dumps(songs_data)
            return render(request,'homelistener.html',{'songs_json': songs_json,'top_songs':top_songs,'artists':artists})




def send_otp(request): 
    if request.method=='POST':
        phone_number=request.POST.get('phone_number')
        if phone_number is None:
            success='Phone number is required'
            return HttpResponse(success)
        
        otp=send_otp_to_phone(phone_number) 
        
        temp=otp_grabber(phone_number=phone_number,otp=otp)
        temp.save()
        print(otp)
        success=f'OTP is sent to {phone_number}'
        return HttpResponse(success)  
    return HttpResponse('Done')



def verify_otp(request): 
    if request.method=='POST':
        try:   
            otp=request.POST.get('otp')
            phone_number=request.POST.get('phone_number_for_verify')
            temp=otp_grabber.objects.filter(phone_number=phone_number,otp=otp).first()
            print(temp)
            if temp is None:
                success='Wrong_OTP'     
             
                return HttpResponse(success)
            else:
                temp.delete()
                olduser=User.objects.filter(phone_number=phone_number).first()
                if olduser is None:
                    temp_email=generate_unique_email(phone_number)
                    if User.objects.filter(email=temp_email,is_listener=True).first():
                        print('Email is Already Taken')
                        return redirect('/')
                    user_obj=User.objects.create(email=temp_email,phone_number=phone_number,is_listener=True)  
                    user_obj.set_password(otp) 
                    user_obj.save()
                    new_profile=l_profile.objects.create(email=temp_email,phone_number=phone_number) 
                    new_profile.save()

                    user=authenticate(email=temp_email,password=otp) 
                    if user is None:
                        messages.success(request,'Wrong Password')
                        return redirect('/')  
                    else:    
                        mylogin(request,user)                   
                        return redirect('/homel')
                else:
                    olduser.set_password(otp)
                    old_email=olduser.email
                    olduser.save()
                    user=authenticate(email=old_email,password=otp) 
                    if user is None:
                        messages.success(request,'Wrong Password')
                        return redirect('/')  
                    else:    
                        mylogin(request,user)                   
                        return redirect('/homel')
        except Exception as e:
            print(e)        
    return HttpResponse('Done')


@login_required
def homel(request):   
            now = datetime.datetime.now()
            hour = now.hour
            print(hour)
            if 5<=hour<12:
                greet='Good Morning'
            else:
                greet='Good Evening'
            profile=l_profile.objects.filter(email=request.user.email).first()
            liked_songs=Song.objects.filter(likes__in=[profile])
            artists=a_profile.objects.all()
            top_songs=Song.objects.all()
            songs_data=[]
            for song in top_songs:
                songs_data.append({
                    'id': song.id,
                    'songName': f'{song.songname}<br><div class="subtitle">{song.singername}</div>',
                    'cover': song.cover.url,
                    'file': song.songfile.url if song.songfile else None
                })  
            songs_json=json.dumps(songs_data)
            return render(request,'homel.html',{'profile':profile,'greet':greet,'songs_json': songs_json,'top_songs':top_songs,'artists':artists,'liked_songs':liked_songs})
                      

def generate_unique_email(prefix):
    unique_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    email = f"{prefix}{unique_id}@phone.com"
    return email.lower()        



def register(request): 
    if request.method=='POST':
        exampleInputEmail1=request.POST.get('exampleInputEmail1')
        exampleInputPassword1=request.POST.get('exampleInputPassword1')
        try:
            if User.objects.filter(email=exampleInputEmail1,is_listener=True).first():
                if l_profile.objects.filter(email=exampleInputEmail1,is_email_verified=True):
                    success='Email is Already Taken'
                    return HttpResponse(success)
                else:
                    success='Already registered ,Check your Mail for verification'
                    return HttpResponse(success)    

                
            user_obj=User.objects.create(email=exampleInputEmail1,is_listener=True)  
            user_obj.set_password(exampleInputPassword1) 
            user_obj.save()
            auth_token=str(uuid.uuid4())
            main=l_profile.objects.create(email=exampleInputEmail1,email_token=auth_token) 
            main.save()
            print('Hello')
            send_email_token(exampleInputEmail1,auth_token,'Listener')
            success=',Please, Check Your Mail Box'
            return HttpResponse(success)
        except Exception as e:
            print(e)
    return HttpResponse('Done')   

        
        


def login(request):
      if request.method=='POST':
        try:
            email=request.POST.get('exampleInputEmail')
            password=request.POST.get('exampleInputPassword')
            print(email,password)
            user_object=User.objects.filter(email=email,is_listener=True).first()
            print(user_object)

            if user_object is None:
                success='Username Not Found'
                return HttpResponse(success)
            else:
                obj=l_profile.objects.filter(email=email).first()
                print('Hello preet')
                if not obj.is_email_verified:
                    success='Email is Not Verified Yet'
                    return HttpResponse(success)

            
                # Authentication with email and password 
                print('Hello guys')
                user=authenticate(email=email,password=password) 
                if user is None:
                    messages.success(request,'Wrong Password')
                    return redirect('/')  
                else:    
                    mylogin(request,user)
                    return redirect('/homel')
                    
        except Exception as e:
            print(e)            
      return HttpResponse('Done')

def custom_logout(request):
    # Clear session data
    request.session.clear()
    return redirect('/') 

@login_required
def search(request):
    if request.method=='POST':
        search=request.POST.get('search')
        songs=Song.objects.filter(Q(singername__icontains=search)|Q(songname__icontains=search))
        if songs:
            artists=a_profile.objects.filter(email=songs[0].singeremail)
            songs_data=[]
            for song in songs:
                songs_data.append({
                    'id': song.id,
                    'songName': f'{song.songname}<br><div class="subtitle">{song.singername}</div>',
                    'cover': song.cover.url,
                    'file': song.songfile.url if song.songfile else None
                })
            songs_json=json.dumps(songs_data)
            return render(request,'search.html',{'songs_json': songs_json,'songs':songs,'artists':artists})
        else:
            success='No Data Found'
            return render(request,'search.html',{'success':success})
    return render(request,'search.html')


def like_song(request,idno):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        user = l_profile.objects.filter(email=request.user.email).first()
        mysong = Song.objects.filter(id=idno).first()
        songs=Song.objects.filter(likes__in=[user])
        
        for song in songs :
            if song==mysong:
                mysong.likes.remove(user)
                success = 'Removed from Liked Songs'
                return JsonResponse({'message': success})
        else:    
            mysong.likes.add(user)
            success = 'Added to your Liked Songs'
            return JsonResponse({'message': success})
    
    success = 'Song was not added successfully'
    return JsonResponse({'message': success})


def follow(request,idno):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        user = l_profile.objects.filter(email=request.user.email).first()
        myprofile = a_profile.objects.filter(email=idno).first()
        profiles=a_profile.objects.filter(follower__in=[user])
        
        for i in profiles :
            if i==myprofile:
                myprofile.follower.remove(user)
                success = 'Removed from following list'
                return JsonResponse({'message': success})
        else:    
            myprofile.follower.add(user)
            success = 'Added to your follower list'
            return JsonResponse({'message': success})
    
    success = 'Singer was not Followed successfully'
    return JsonResponse({'message': success})


def liked_songs(request):
        b = l_profile.objects.filter(email=request.user.email).first()
        songs=Song.objects.filter(likes__in=[b])
        print(songs)
        if songs:
            songs_data=[]
            count=1
            for song in songs:
                songs_data.append({
                    'id': count,
                    'songName': f'{song.songname}<br><div class="subtitle">{song.singername}</div>',
                    'cover': song.cover.url,
                    'file': song.songfile.url if song.songfile else None
                })
                count+=1
            
            songs_json=json.dumps(songs_data)
            return render(request,'liked_songs.html',{'songs_json': songs_json,'songs':songs})
        else:
            success='No Data Found'
            return render(request,'homel.html',{'success':success})
    # return render(request,'liked_songs.html')




def talk(engine,text):
        engine.setProperty('rate', 150) 
        engine.say(text)
        engine.runAndWait()



def hey_dimmy_command_getter():
        try:
            listener = sr.Recognizer()
            engine=pyttsx3.init()
            with sr.Microphone() as source:
                print('Listening...')
                listener.adjust_for_ambient_noise(source)
                voice = listener.listen(source, timeout=2)
                command = listener.recognize_google(voice)
                search = command.lower().strip()
                print(search)
                if 'play' in search:
                    search=search.replace('play','').strip()
                 
                    print(search)
                    songs=Song.objects.filter(Q(singername__icontains=search)|Q(songname__icontains=search))
                    print(songs)
                    songs_data = []
                    count = 1
                    for song_obj in songs:
                            songs_data.append({
                                'id': count,
                                'songName': f'{song_obj.songname}<br><div class="subtitle">{song_obj.singername}</div>',
                                'cover': song_obj.cover.url,
                                'file': song_obj.songfile.url if song_obj.songfile else None
                            })
                            count += 1
                        
                    songs_json = json.dumps(songs_data)
                    return songs_json

                elif 'time' in command:
                    time=datetime.datetime.now().strftime('%I:%M %p')
                    talk(engine,'Current Time is :'+time)
                    return t

                elif 'joke' in command:
                    command=command.replace('joke','')
                    x=pyjokes.get_joke()
                    talk(engine,x)  
                    return j
                
                

                            
                    
                # return None  # If the wake word is detected, but no valid command is recognized
        except sr.UnknownValueError:
            talk(engine, 'Sorry, I could not understand. Please try again.')
            
        except sr.RequestError:
            talk(engine, 'Sorry, there was an issue with the speech recognition service. Please try again later.')
            
        except Exception as e:
            print(e)
            talk(engine, 'check your internet connection')
            

def take_command1(engine):
    
    listener=sr.Recognizer()
    print('I am take command from process')
    voices=engine.getProperty('voices')
    engine.setProperty('voice',voices[1].id)

    # songs = Song.objects.all()
    # print(songs)
    try:
      with sr.Microphone() as source:
         print('Listening... Preet')
         listener.adjust_for_ambient_noise(source)
         voice = listener.listen(source,timeout=5)
         command = listener.recognize_google(voice)
         command=command.lower()
         
         print(command,'Ram ram')
         if 'alexa' in command:
            command=command.replace('alexa','')    #it does not print its name 
            return command
    except sr.UnknownValueError:
        talk(engine, 'Sorry, I could not understand. Please try again.')
    

    except sr.RequestError:
        talk(engine, 'Sorry, there was an issue with the speech recognition service. Please try again later.')


    except Exception as e:
        print(e)
        talk(engine, 'An error occurred. Please try again.')

engine=pyttsx3.init()


def your_bb(request):
    process_audio()
    talk(engine,'Welcome to Bitbuzz')
    command=take_command1(engine)
    print(command)
    if command :
        if 'play' in command:
            song = command.replace('play', '').strip()
            talk(engine, 'Playing ' + song)
            
            songs = Song.objects.all()
            matched_songs = []
            
            # Iterate over all songs and calculate Levenshtein distance
            for song_obj in songs:
                singer_distance = Levenshtein.distance(song_obj.singername.lower(), song.lower())
                song_distance = Levenshtein.distance(song_obj.songname.lower(), song.lower())
                
                # Adjust the threshold according to your preference
                if singer_distance <= 2 or song_distance <= 2:
                    matched_songs.append(song_obj)
            print('fizzy algo',matched_songs)
            if matched_songs:
                songs_data = []
                count = 1
                
                # Iterate over matched songs
                for song_obj in matched_songs:
                    songs_data.append({
                        'id': count,
                        'songName': f'{song_obj.songname}<br><div class="subtitle">{song_obj.singername}</div>',
                        'cover': song_obj.cover.url,
                        'file': song_obj.songfile.url if song_obj.songfile else None
                    })
                    count += 1
                
                songs_json = json.dumps(songs_data)
                return JsonResponse({'songs_json': songs_json})
            
        else:
            talk(engine, 'Sorry, no songs found.')
            return render(request, 'homel.html', {'success': success})
       
    else:
        # talk(engine,'i does not understand try again') 
        pass
    return JsonResponse('Function executed successfully', safe=False)