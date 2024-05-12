import speech_recognition as sr
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from Artists.models import Song
from .views import talk
import pyttsx3
from channels.generic.websocket import WebsocketConsumer


class TakeCommandConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "group_name",  # Replace with the appropriate group name
            self.channel_name
        )
        print(self.channel_name)
        await self.accept()
        self.engine = pyttsx3.init()
        self.listener = sr.Recognizer()
        print('I am take command') 
        await self.send(text_data=json.dumps(
            {'message' : 'Hey my name is preet'}
        ))

    async def disconnect(self, close_code):
        print('Disconnetcted')


    async def receive(self, text_data):
        print(text_data)
        data=json.loads(text_data)
        data['name']='preet'
        self.send(text_data=json.dumps(data))


    async def my_custom_function(self,event):
        data=json.dumps(event)

        print('Hello')
        await self.send(text_data=data)
        print('done')





