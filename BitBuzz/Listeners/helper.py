import requests
import random
from django.conf import settings
from threading import *
def send_otp_to_phone(phone_number):
    try:
        otp=random.randint(1000,9999)
        url=f'https://2factor.in/API/V1/{settings.API_KEY}/SMS/{phone_number}/{otp}'
        response=requests.get(url)
        return otp
    except Exception as e:
        return None


class CustomThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
 
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
             
    def join(self, *args):
        Thread.join(self, *args)
        return self._return