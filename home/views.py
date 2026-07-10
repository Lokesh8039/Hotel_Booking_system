from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime

from django.db.models import Avg, Q
from django.core.paginator import Paginator
from accounts.models import Hotel, HotelUser, HotelBooking, Ameneties, Wishlist


def index(request):
    hotels = Hotel.objects.all().annotate(avg_rating=Avg('reviews__rating'))

    # Search by hotel name or location
    search_query = request.GET.get('search', '')
    if search_query:
        hotels = hotels.filter(
            Q(hotel_name__icontains=search_query) | 
            Q(hotel_location__icontains=search_query)
        )

    # Filter by Location Dropdown
    location_filter = request.GET.get('location', '')
    if location_filter:
        hotels = hotels.filter(hotel_location__icontains=location_filter)

    # Filter by Price Range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        hotels = hotels.filter(hotel_offer_price__gte=min_price)
    if max_price:
        hotels = hotels.filter(hotel_offer_price__lte=max_price)

    # Filter by Amenities (AND query)
    selected_amenities = request.GET.getlist('amenities')
    if selected_amenities:
        for amenity_id in selected_amenities:
            hotels = hotels.filter(ameneties__id=amenity_id)

    # Sorting logic
    sort_by = request.GET.get('sort_by')
    if sort_by == "sort_low":
        hotels = hotels.order_by('hotel_offer_price')
    elif sort_by == "sort_high":
        hotels = hotels.order_by('-hotel_offer_price')
    elif sort_by == "sort_rating":
        hotels = hotels.order_by('-avg_rating')

    # Get user details and wishlist
    wishlisted_hotel_ids = []
    user_name = "Guest"
    if request.user.is_authenticated:
        try:
            hotel_user = HotelUser.objects.get(id=request.user.id)
            user_name = hotel_user.first_name
            wishlisted_hotel_ids = list(Wishlist.objects.filter(user=hotel_user).values_list('hotel_id', flat=True))
        except HotelUser.DoesNotExist:
            pass

    # Pagination: 8 hotels per page
    paginator = Paginator(hotels.distinct(), 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # General metadata for filters
    all_amenities = Ameneties.objects.all()
    # Get distinct locations (simplified by taking unique location field entries)
    all_locations = Hotel.objects.values_list('hotel_location', flat=True).distinct()
    all_locations = sorted(list(set(loc.split(',')[0].strip() for loc in all_locations if loc)))

    context = {
        'page_obj': page_obj,
        'user': user_name,
        'all_amenities': all_amenities,
        'all_locations': all_locations,
        'wishlisted_hotel_ids': wishlisted_hotel_ids,
        'search_query': search_query,
        'location_filter': location_filter,
        'min_price': min_price,
        'max_price': max_price,
        'selected_amenities': [int(a) for a in selected_amenities],
        'sort_by': sort_by
    }
    return render(request, 'index.html', context=context)




from accounts.models import RoomType, Review, PromoCode
from datetime import date

def hotel_details(request, slug):
    hotel = Hotel.objects.get(hotel_slug=slug)
    reviews = hotel.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0

    try:
        hotel_user = HotelUser.objects.get(id=request.user.id)
        user_name = hotel_user.first_name
    except HotelUser.DoesNotExist:
        user_name = None

    if request.method == "POST":
        # Check if it is a review submission
        if "rating" in request.POST:
            if not request.user.is_authenticated:
                messages.warning(request, "You must be logged in to leave a review.")
                return redirect("login_page")
            
            try:
                hotel_user = HotelUser.objects.get(id=request.user.id)
                rating = int(request.POST.get('rating'))
                comment = request.POST.get('comment')
                Review.objects.create(
                    hotel=hotel,
                    user=hotel_user,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, "Review added successfully!")
            except Exception as e:
                messages.error(request, f"Error saving review: {e}")
            return redirect(request.path_info)

        # Otherwise, handle hotel booking submission
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        room_type_id = request.POST.get('room_type')

        if not start_date or not end_date or not room_type_id:
            messages.warning(request, "Please fill in all booking fields.")
            return redirect(request.path_info)

        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        days_count = (end_date_dt - start_date_dt).days

        if days_count <= 0:
            messages.warning(request, "Invalid Booking Date range selected.")
            return redirect(request.path_info)

        # Check room availability
        try:
            room_type = RoomType.objects.get(id=room_type_id, hotel=hotel)
        except RoomType.DoesNotExist:
            messages.error(request, "Selected room type is invalid.")
            return redirect(request.path_info)

        active_bookings_count = HotelBooking.objects.filter(
            room_type=room_type,
            booking_start_date__lt=end_date_dt,
            booking_end_date__gt=start_date_dt
        ).exclude(status='Cancelled').count()

        if active_bookings_count >= room_type.total_rooms:
            messages.warning(request, f"No availability in {room_type.name} for the selected dates.")
            return redirect(request.path_info)

        # Base price calculation
        amount = room_type.price * days_count

        # Validate Promo Code
        promo_code_str = request.POST.get('promo_code', '').strip().upper()
        promo_id = ""
        if promo_code_str:
            try:
                promo = PromoCode.objects.get(code=promo_code_str, active=True, valid_until__gte=date.today())
                discount = (promo.discount_percentage / 100.0) * amount
                amount = max(0.0, amount - discount)
                promo_id = promo.id
                messages.success(request, f"Promo code applied! Saved ₹{discount:.2f}")
            except PromoCode.DoesNotExist:
                messages.warning(request, "Invalid or expired promo code.")

        return redirect(f"/account/payment/?amount={amount}&start_date={start_date}&end_date={end_date}&hotel_id={hotel.id}&room_type_id={room_type.id}&promo_id={promo_id}")

    room_types = hotel.room_types.all()

    context = {
        'hotel': hotel,
        'user': user_name,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'room_types': room_types
    }
    return render(request, 'hotel_detail.html', context)