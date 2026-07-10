from django.shortcuts import render,redirect ,HttpResponse,HttpResponseRedirect
from .models import HotelUser , HotelVendor,Hotel,Ameneties,HotelImages,HotelBooking
from django.db.models import Q
from django.contrib import messages
from .utils import generateRandomToken,sendEmailToken,sendOTPtoEmail,sendEmailToken_vendor,generateSlug
from django.contrib.auth import authenticate ,login,logout
from django.contrib.auth.decorators import login_required
import random
from django.core.mail import send_mail
def login_page(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'hoteluser'):
            return redirect("/")
        else:
            logout(request)
    if request.method == "POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        hotel_user = HotelUser.objects.filter(email = email).first()
        if not hotel_user:
            messages.warning(request, "Account Not Found")
            return redirect("login_page")
        if not hotel_user.is_verified:
            messages.warning(request, "Account Not Verified")
            return redirect("login_page")
        hotel_user = authenticate(username=hotel_user.username,password = password)
        if hotel_user:
            login(request,hotel_user)
            messages.success(request, "Account Login Success")
            return redirect("/")
        messages.warning(request, "Account Password is Wrong")
        return redirect("login_page")

    return render(request , "login.html")



def register(request):
    if request.method == "POST":
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        password=request.POST.get('password')
        
        phone_number=request.POST.get('phone_number')
        
        hotel_user = HotelUser.objects.filter(Q(email = email) | Q(phone_number = phone_number) )
        if hotel_user.exists():
            messages.warning(request, "Your account exists with This Phone Number and Email")
            return redirect("register")
        hotel_user=HotelUser.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email= email,
            phone_number = phone_number,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()
        sendEmailToken(email,hotel_user.email_token)
        messages.success(request, "Account Created.Email Sent to your mail")
        return redirect("register")
    return render(request , "register.html")


def verifyEmail(request,token):
    try:
        hotel_user = HotelUser.objects.get(email_token=token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Email Verified.Please Login")
        return redirect("login_page")
    except Exception as e:
        return HttpResponse(request , "Token INVALID")
    



def send_otp(request, email):
    hotel_user = HotelUser.objects.filter(email=email).first()
    if not hotel_user:
        messages.warning(request, "No Account Found.")
        return redirect('/account/login/')
    if not hotel_user.is_verified:
        messages.warning(request, "Account Not Verified")
        return redirect("login_page")     

    otp = random.randint(1000, 9999)
    hotel_user.otp = otp
    hotel_user.save()

    sendOTPtoEmail(email, otp)
    messages.success(request, f"OTP Sent To {email}.")
    return redirect(f'/account/verify-otp/{email}/')

def verify_otp(request , email):
    if request.method == "POST":
        otp  = request.POST.get('otp')
        hotel_user = HotelUser.objects.get(email = email)

        if otp == hotel_user.otp:
            messages.success(request, "OTP Verified Login Success")
            login(request , hotel_user)
            return redirect('/account/login/')

        messages.warning(request, "Wrong OTP")
        return redirect(f'/account/verify-otp/{email}/')

    return render(request , 'verify_otp.html')


def login_vendor(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'hotelvender'):
            return redirect("dashboard")
        else:
            logout(request)
        
    if request.method == "POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        hotel_user = HotelVendor.objects.filter(username=email).first()
        if not hotel_user:
            messages.warning(request, "Account Not Found")
            return redirect("login_vendor")
        if not hotel_user.is_verified:
            messages.warning(request, "Account Not Verified")
            return redirect("login_vendor")
        hotel_user = authenticate(username=hotel_user.username, password=password)
        if hotel_user:
            messages.success(request, "Account Login Success")
            login(request,hotel_user)
            return redirect("dashboard")
        messages.warning(request, "Incorrect Password")
        return redirect("login_vendor")

    return render(request , "vendor/login_vendor.html")

def register_vendor(request):
    if request.method == "POST":
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        business_name = request.POST.get('business_name')
        email=request.POST.get('email')
        password=request.POST.get('password')
        phone_number=request.POST.get('phone_number')
        
        hotel_user = HotelVendor.objects.filter(Q(username = email) | Q(phone_number = phone_number))
        if hotel_user.exists():
            messages.warning(request, "Your account exists with This Phone Number and Email")
            return redirect("register_vendor")
        hotel_user=HotelVendor.objects.create(
            username = email,
            first_name = first_name,
            last_name = last_name,
            business_name = business_name,
            email= email,
            phone_number = phone_number,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()
        sendEmailToken_vendor(email,hotel_user.email_token)
        messages.success(request, "Email Sent to your mail")
        return redirect("register_vendor")
    return render(request , "vendor/register_vendor.html")



def send_otp_vendor(request, email):
    hotel_user = HotelVendor.objects.filter(username=email).first()
    if not hotel_user:
        messages.warning(request, "No Account Found.")
        return redirect('/account/login/')
    if not hotel_user.is_verified:
        messages.warning(request, "Account Not Verified")
        return redirect("login_vendor")

    otp = random.randint(1000, 9999)
    hotel_user.otp = otp
    hotel_user.save()

    sendOTPtoEmail(email, otp)
    messages.success(request, f"OTP Sent To {email}.")
    return redirect(f'/account/verify-otp_vendor/{email}/')

def verify_otp_vendor(request , email):
    if request.method == "POST":
        otp  = request.POST.get('otp')
        hotel_user = HotelVendor.objects.get(username = email)

        if otp == hotel_user.otp:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('dashboard')

        messages.warning(request, "Wrong OTP")
        return redirect(f'/account/verify-otp_vendor/{email}/')

    return render(request , 'vendor/verifyotp.html')



def verifyEmail_vendor(request,token):
    try:
        hotel_user = HotelVendor.objects.get(email_token=token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Email Verified.Please Login")
        return redirect("login_vendor")
    except Exception as e:
        return HttpResponse(request , "Token INVALID")
    



@login_required(login_url='login_vendor')
def dashboard(request):
    from django.db.models import Sum
    import datetime
    
    hotel_vendor = HotelVendor.objects.get(id=request.user.id)
    hotelbook = Hotel.objects.filter(hotel_owner=hotel_vendor.id)
    hotelbooking = HotelBooking.objects.filter(hotel__in=hotelbook)
    
    user_name = hotel_vendor.first_name
    
    # Calculate key metrics
    total_bookings = hotelbooking.count()
    total_revenue = hotelbooking.exclude(status='Cancelled').aggregate(Sum('price'))['price__sum'] or 0.0
    cancelled_bookings = hotelbooking.filter(status='Cancelled').count()
    
    # Generate 6-month historical chart data
    months_labels = []
    monthly_revenue = []
    monthly_bookings = []
    
    today = datetime.date.today()
    for i in range(5, -1, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        
        month_start = datetime.date(year, month, 1)
        if month == 12:
            month_end = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            month_end = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
            
        month_bookings_qs = hotelbooking.filter(booking_start_date__gte=month_start, booking_start_date__lte=month_end)
        month_confirmed = month_bookings_qs.exclude(status='Cancelled')
        
        months_labels.append(month_start.strftime("%b %y"))
        monthly_bookings.append(month_bookings_qs.count())
        monthly_revenue.append(float(month_confirmed.aggregate(Sum('price'))['price__sum'] or 0.0))
        
    context = {
        'hotels': Hotel.objects.filter(hotel_owner=request.user),
        'user': user_name,
        'hotelbook': hotelbooking.order_by('-booking_start_date'),
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'cancelled_bookings': cancelled_bookings,
        'months_labels': months_labels,
        'monthly_revenue': monthly_revenue,
        'monthly_bookings': monthly_bookings,
        'today': datetime.date.today(),
    }
    return render(request, 'vendor/vendor_dashboard.html', context)




def logout_user(request):
    logout(request)
    messages.success(request, "Logout Success")
    return redirect("login_page")



def logout_vendor(request):
    logout(request)
    return redirect("login_vendor")






@login_required(login_url='login_vendor')
def add_hotel(request):
    hotel_vendor = HotelVendor.objects.get(id = request.user.id)
    user_name = hotel_vendor.first_name
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        ameneties= request.POST.getlist('ameneties')
        hotel_price= request.POST.get('hotel_price')
        hotel_offer_price= request.POST.get('hotel_offer_price')
        hotel_location= request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)

        hotel_vendor = HotelVendor.objects.get(id = request.user.id)

        hotel_obj = Hotel.objects.create(
            hotel_name = hotel_name,
            hotel_description = hotel_description,
            hotel_price = hotel_price,
            hotel_offer_price = hotel_offer_price,
            hotel_location = hotel_location,
            hotel_slug = hotel_slug,
            hotel_owner = hotel_vendor
        )

        for ameneti in ameneties:
            ameneti = Ameneties.objects.get(id = ameneti)
            hotel_obj.ameneties.add(ameneti)
            hotel_obj.save()


        messages.success(request, "Hotel Added Sucessfully")
        return redirect('/account/dashboard/')


    ameneties = Ameneties.objects.all()
        
    return render(request, 'vendor/add_hotel.html', context = {'ameneties' : ameneties,'user':user_name})


@login_required(login_url='login_vendor')
def delete_image(request, id):

    hotel_image = HotelImages.objects.get(id = id)
    hotel_image.delete()
    messages.success(request, "Hotel Image deleted")
    return redirect('/account/dashboard/')


@login_required(login_url='login_vendor')
def upload_images(request, slug):
    hotel_vendor = HotelVendor.objects.get(id = request.user.id)
    user_name = hotel_vendor.first_name
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.method == "POST":
        image = request.FILES['image']
        HotelImages.objects.create(
        hotel = hotel_obj,
        image = image
        )
        return HttpResponseRedirect(request.path_info)

    return render(request, 'vendor/upload_images.html', context = {'images' : hotel_obj.hotel_images.all(),'user':user_name,'slug':slug})



@login_required(login_url='login_vendor')
def delete_image(request, id,slug):
    hotel_image = HotelImages.objects.get(id = id)
    hotel_image.delete()
    messages.success(request, "Hotel Image deleted")
    return redirect(f'/account/upload-images/{slug}')



@login_required(login_url='login_vendor')
def edit_hotel(request, slug):
    hotel_vendor = HotelVendor.objects.get(id = request.user.id)
    user_name = hotel_vendor.first_name
    hotel_obj = Hotel.objects.get(hotel_slug=slug)
    
    if request.user.id != hotel_obj.hotel_owner.id:
        return HttpResponse("You are not authorized")

    if request.method == "POST":
 
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        
        hotel_obj.hotel_name = hotel_name
        hotel_obj.hotel_description = hotel_description
        hotel_obj.hotel_price = hotel_price
        hotel_obj.hotel_offer_price = hotel_offer_price
        hotel_obj.hotel_location = hotel_location
        hotel_obj.save()
        
        messages.success(request, "Hotel Details Updated")

        return HttpResponseRedirect(request.path_info)

    ameneties = Ameneties.objects.all()
    
    return render(request, 'vendor/edit_hotel.html', context={'hotel': hotel_obj, 'ameneties': ameneties,'user':user_name})


def delete_booking(request,id):
    import datetime
    try:
        delete = HotelBooking.objects.get(id=id)
        if delete.booking_start_date <= datetime.date.today():
            messages.warning(request, "Cannot cancel reservations that have already started or are in the past.")
            return redirect('dashboard')
        delete.delete()
        messages.success(request, "Hotel Booking Deleted")
    except HotelBooking.DoesNotExist:
        messages.error(request, "Booking not found.")
    return redirect('dashboard')

import razorpay
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import HotelBooking, HotelUser, Hotel, RoomType, PromoCode
from datetime import datetime

def payment(request):
    amount = request.GET.get('amount')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    hotel_id = request.GET.get('hotel_id')
    room_type_id = request.GET.get('room_type_id', '')
    promo_id = request.GET.get('promo_id', '')

    if not amount or not hotel_id:
        return render(request, 'error.html', {'message': 'Invalid payment request'})

    amount_int = int(float(amount) * 100)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment_order = client.order.create({'amount': amount_int, 'currency': 'INR', 'payment_capture': 1})

    return render(request, 'payment.html', {
        'payment': payment_order,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount_int,
        'start_date': start_date,
        'end_date': end_date,
        'hotel_id': hotel_id,
        'room_type_id': room_type_id,
        'promo_id': promo_id
    })


@csrf_exempt
def payment_success(request):
    hotel_id = request.GET.get('hotel_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    room_type_id = request.GET.get('room_type_id')
    promo_id = request.GET.get('promo_id')
    order_id = request.GET.get('order_id', '')
    payment_id = request.GET.get('payment_id', '')

    if hotel_id and request.user.is_authenticated:
        hotel = Hotel.objects.get(id=hotel_id)
        user = HotelUser.objects.get(id=request.user.id)
        
        room_type = None
        if room_type_id:
            room_type = RoomType.objects.get(id=room_type_id)
            
        promo = None
        if promo_id:
            promo = PromoCode.objects.get(id=promo_id)

        days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days
        base_price = (room_type.price if room_type else hotel.hotel_offer_price) * days
        total_price = base_price
        if promo:
            total_price = base_price * (1 - (promo.discount_percentage / 100.0))

        booking = HotelBooking.objects.create(
            hotel=hotel,
            booking_user=user,
            room_type=room_type,
            booking_start_date=start_date,
            booking_end_date=end_date,
            price=total_price,
            status='Confirmed',
            razorpay_order_id=order_id,
            razorpay_payment_id=payment_id,
            applied_promo=promo
        )
        
        room_name = room_type.name if room_type else "Standard Room"
        subject = f"Booking Confirmation - {hotel.hotel_name}"
        message = (
            f"Hello {user.first_name},\n\n"
            f"Your booking for '{hotel.hotel_name}' has been confirmed!\n"
            f"🏠 Room Type: {room_name}\n"
            f"📍 Location: {hotel.hotel_location}\n"
            f"🗓️ From: {start_date}\n"
            f"🗓️ To: {end_date}\n"
            f"💰 Total Amount Paid: ₹{total_price:.2f}\n\n"
            f"Thank you for choosing our service!\n\n"
            f"- Team Hotel Booking System"
        )

        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
        messages.success(request, "Booking Success! Confirmation sent to your email.")

    return redirect('/')


@login_required(login_url='login_page')
def my_bookings(request):
    import datetime
    try:
        hotel_user = HotelUser.objects.get(id=request.user.id)
        user_name = hotel_user.first_name
        bookings = HotelBooking.objects.filter(booking_user=hotel_user).order_by('-booking_start_date')
    except HotelUser.DoesNotExist:
        messages.error(request, "Account not found.")
        return redirect('/')
    
    return render(request, 'my_bookings.html', {
        'bookings': bookings,
        'user': user_name,
        'today': datetime.date.today()
    })


@login_required(login_url='login_page')
def cancel_booking(request, id):
    import datetime
    try:
        booking = HotelBooking.objects.get(id=id, booking_user__id=request.user.id)
        
        if booking.status == 'Cancelled':
            messages.warning(request, "This booking is already cancelled.")
            return redirect('my_bookings')

        # Check if booking start date is today or in the past
        if booking.booking_start_date <= datetime.date.today():
            messages.warning(request, "Cannot cancel bookings that have already started or are in the past.")
            return redirect('my_bookings')
            
        refunded = False
        if booking.razorpay_payment_id:
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                refund_amount = int(booking.price * 100)
                client.payment.refund(booking.razorpay_payment_id, {"amount": refund_amount})
                refunded = True
            except Exception as e:
                print(f"Razorpay refund failed: {e}")

        booking.status = 'Cancelled'
        booking.save()
        
        if refunded:
            messages.success(request, "Booking cancelled and refund initiated successfully!")
        else:
            messages.success(request, "Booking cancelled successfully! Refund will be processed offline if applicable.")
            
    except HotelBooking.DoesNotExist:
        messages.error(request, "Booking not found or not authorized.")
        
    return redirect('my_bookings')



@login_required(login_url='login_page')
def toggle_wishlist(request, id):
    from .models import Wishlist
    try:
        hotel = Hotel.objects.get(id=id)
        hotel_user = HotelUser.objects.get(id=request.user.id)
        
        wish, created = Wishlist.objects.get_or_create(user=hotel_user, hotel=hotel)
        if not created:
            wish.delete()
            messages.info(request, f"Removed {hotel.hotel_name} from your wishlist.")
        else:
            messages.success(request, f"Added {hotel.hotel_name} to your wishlist!")
            
    except Exception as e:
        messages.error(request, "Error updating wishlist.")
        
    next_url = request.GET.get('next', '/')
    return redirect(next_url)


@login_required(login_url='login_page')
def wishlist_view(request):
    from .models import Wishlist
    from django.db.models import Avg
    try:
        hotel_user = HotelUser.objects.get(id=request.user.id)
        user_name = hotel_user.first_name
        wishlist_items = Wishlist.objects.filter(user=hotel_user).select_related('hotel')
        hotels = [item.hotel for item in wishlist_items]
        
        # Annotate rating for rendering
        for hotel in hotels:
            reviews = hotel.reviews.all()
            hotel.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    except HotelUser.DoesNotExist:
        messages.error(request, "Account not found.")
        return redirect('/')
        
    return render(request, 'wishlist.html', {'hotels': hotels, 'user': user_name})


def check_promo(request):
    from django.http import JsonResponse
    import datetime
    code = request.GET.get('code', '').strip().upper()
    if not code:
        return JsonResponse({'valid': False, 'message': 'No code provided.'})
        
    try:
        promo = PromoCode.objects.get(code=code, active=True, valid_until__gte=datetime.date.today())
        return JsonResponse({
            'valid': True,
            'code': promo.code,
            'discount_percentage': promo.discount_percentage,
            'promo_id': promo.id
        })
    except PromoCode.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Invalid or expired promo code.'})

