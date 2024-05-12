from django.urls import path
from .views import *
urlpatterns=[
    path('',Artists,name='Artists'),
    path('Music/',Music,name='Music'),
    path('edit',edit,name='edit'),
    path('songedit',songedit,name='songedit'),
    path('deletesong/<int:id>/',deletesong,name="deletesong"),
    path('follower_data_api', follower_data_api, name='follower_data_api'),
]