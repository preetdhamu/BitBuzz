from django.urls import path
from Accounts import views
from .views import ContinueWithGoogleView
urlpatterns=[
    path('',views.login,name='login'),
    path('register/',views.register,name='register'),
    # path('artists/',views.artists_home,name='artists_home'),
    path('verify/<str:token>/<str:value>',views.verify,name='verify'),
    path('ContinueWithGoogleView/', ContinueWithGoogleView.as_view(), name='ContinueWithGoogleView'),
    # path('logout',views.logout_view),
    path('forget/',views.forget,name="forget"),
    path('forget_otp/',views.forget_otp,name="forget_otp"),
    path('new_pass/<str:email>',views.new_pass,name="new_pass"),
    path('verify_pass_code/<str:email>/<int:otp>',views.verify_pass_code,name="verify_pass_code"),
]