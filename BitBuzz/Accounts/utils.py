from django.conf import settings
from django.core.mail import send_mail
def send_email_token(email,token,value):
    try:
        subject='BITBUZZ, Your Account needs to be verified'
        message=f"Click on the link to verify http://127.0.0.1:8000/accounts/verify/{token}/{value}"
        email_from=settings.EMAIL_HOST_USER
        recipient_list=[email,]
        send_mail(subject,message,email_from,recipient_list)
        print("Mail send successfully")
    except Exception as e:
        print(e)
        return False
    return True

def send_email_otp(email,otp):
    try:
        subject=' BITBUZZ, Your Forget Password OTP '
        message=f"Your Otp is  {otp}"
        email_from=settings.EMAIL_HOST_USER
        recipient_list=[email,]
        send_mail(subject,message,email_from,recipient_list)

    except Exception as e:
        print(e)
        return False
    return True
