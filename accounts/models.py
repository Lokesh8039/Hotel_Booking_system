from django.db import models
from django.contrib.auth.models import User
class HotelUser(User):
    profile_picture = models.ImageField(upload_to="profile")
    phone_number =  models.CharField(unique = True , max_length= 100)
    email_token = models.CharField(max_length = 100 ,null = True , blank=True)
    otp = models.CharField(max_length = 10 , null = True , blank = True)
    is_verified = models.BooleanField(default = False)

    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = "Hotel User"


class HotelVendor(User):
    phone_number =  models.CharField(unique = True, max_length= 100)
    profile_picture = models.ImageField(upload_to="profile")
    email_token = models.CharField(max_length = 100 ,null = True , blank=True)
    otp = models.CharField(max_length = 10 , null = True , blank = True)
    business_name = models.CharField(max_length=100)

    is_verified = models.BooleanField(default = False)

    class Meta:
        db_table = "Hotel Vendor"


class Ameneties(models.Model):
    name = models.CharField(max_length = 1000)
    icon = models.ImageField(upload_to="hotels")

    def __str__(self):
        return self.name

class Hotel(models.Model):
    hotel_name  = models.CharField(max_length = 100)
    hotel_description = models.TextField()
    hotel_slug = models.SlugField(max_length = 1000 , unique  = True)
    hotel_owner = models.ForeignKey(HotelVendor, on_delete = models.CASCADE , related_name = "hotels")
    ameneties = models.ManyToManyField(Ameneties)
    hotel_price = models.FloatField()
    hotel_offer_price = models.FloatField()
    hotel_location = models.TextField()
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return self.hotel_name



class HotelImages(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete = models.CASCADE , related_name = "hotel_images")
    image = models.ImageField(upload_to="hotels")

    def __str__(self):
        return self.hotel.hotel_name

# class HotelManager(models.Model):
#     hotel = models.ForeignKey(Hotel, on_delete = models.CASCADE , related_name = "hotel_managers")
#     manager_name = models.CharField(max_length = 100)
#     manager_contact = models.CharField(max_length = 100)


# class Amenities(models.Model):
#     name = models.CharField(max_length=100)
#     icon = models.ImageField(upload_to='amenities')

#     def __str__(self):
#         return self.name


class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="room_types")
    name = models.CharField(max_length=100)
    price = models.FloatField()
    capacity = models.IntegerField(default=2)
    total_rooms = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.hotel.hotel_name} - {self.name}"

class Review(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(HotelUser, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.hotel_name} ({self.rating}★)"

class Wishlist(models.Model):
    user = models.ForeignKey(HotelUser, on_delete=models.CASCADE, related_name="wishlist")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'hotel')

    def __str__(self):
        return f"{self.user.username} - {self.hotel.hotel_name}"

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.FloatField(default=0.0)
    active = models.BooleanField(default=True)
    valid_until = models.DateField()

    def __str__(self):
        return self.code

class HotelBooking(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete = models.CASCADE , related_name="bookings" )
    booking_user = models.ForeignKey(HotelUser, on_delete = models.CASCADE )
    room_type = models.ForeignKey(RoomType, on_delete = models.SET_NULL, related_name="bookings", null=True, blank=True)
    booking_start_date = models.DateField()
    booking_end_date = models.DateField()
    price = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Confirmed', 'Confirmed'),
            ('Cancelled', 'Cancelled'),
            ('Completed', 'Completed')
        ],
        default='Confirmed'
    )
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    applied_promo = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)