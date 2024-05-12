# """
# ASGI config for BitBuzz project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter,URLRouter
# from Listeners.consumers import TakeCommandConsumer
# from django.urls import path

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BitBuzz.settings')

# # application = get_asgi_application()

# websocket_urlpatterns = [
#     path('ws/take/', TakeCommandConsumer.as_asgi()),
# ]

# application=ProtocolTypeRouter
# (
#     {
#         'http':get_asgi_application(),
#         'websocket':URLRouter
#         (
#            websocket_urlpatterns
#         ),
#     }
# )

"""
ASGI config for BitBuzz project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from Listeners.consumers import TakeCommandConsumer
from django.urls import path
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BitBuzz.settings')

# Define the WebSocket URL patterns
websocket_urlpatterns = [
    path('ws/take/', TakeCommandConsumer.as_asgi()),
]

# Define the ProtocolTypeRouter
application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)



