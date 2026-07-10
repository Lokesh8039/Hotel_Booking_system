import uuid
import threading
import socket
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify
from .models import Hotel

def generateRandomToken():
    return str(uuid.uuid4())

def send_mail_async(subject, message, from_email, recipient_list, fail_silently=True):
    def _send():
        # Set a reasonable connection timeout for SMTP socket
        old_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(10.0)
            send_mail(subject, message, from_email, recipient_list, fail_silently=fail_silently)
        except Exception as e:
            print(f"Async email sending failed: {str(e)}")
        finally:
            socket.setdefaulttimeout(old_timeout)
            
    thread = threading.Thread(target=_send)
    thread.daemon = True
    thread.start()

def sendEmailToken(email, token):
    subject = "Verify Your Email Address"
    message = f"""Hi, please verify your email account by clicking this link: 
    https://hotel-booking-system.onrender.com/account/verify-account/{token}
    """
    send_mail_async(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=True)

def sendEmailToken_vendor(email, token):
    subject = "Verify Your Email Address"
    message = f"""Hi, please verify your email account by clicking this link: 
    https://hotel-booking-system.onrender.com/account/verify-account_vendor/{token}
    """
    send_mail_async(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=True)

def sendOTPtoEmail(email , otp):
    subject = "OTP for Account Login"
    message = f"""Hi, use this OTP to login
     {otp} 
    
    """
    send_mail_async(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=True)

def generateSlug(hotel_name):
    slug = f"{slugify(hotel_name)}-" + str(uuid.uuid4()).split('-')[0]
    if Hotel.objects.filter(hotel_slug = slug).exists():
        return generateSlug(hotel_name)
    return slug
