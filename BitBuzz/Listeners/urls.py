from django.urls import path
from Listeners import views

urlpatterns=[
    path('',views.homelistener),
    path('homel/',views.homel,name='homel'),
    path('liked_songs/',views.liked_songs,name='liked_songs'),
    path('homel/search/',views.search,name='search'),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('send_otp',views.send_otp,name='send_otp'),
    path('verify_otp',views.verify_otp,name='verify_otp'),
    path('custom_logout/',views.custom_logout,name='custom_logout'),
    path('homel/your_bb',views.your_bb,name='your_bb'),
    path('like_song/<int:idno>',views.like_song,name='like_song'),
    path('follow/<str:idno>',views.follow,name='follow'),
]