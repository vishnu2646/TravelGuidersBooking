from django.urls import path
from .views import *

urlpatterns = [
    path('location/', getGuidersByLocation, name='location'),
    path('places/', getGuidersByLocationAndName, name='places'),
    path('guiders/', getAllGuides, name='guiders'),
    path('guiders/<int:id>', getGuideDetails, name='guiders'),
    path('create/travelplace/', createTravelPlace, name='create-travel-places'),
    path('travelplaces/', getAllTravelPlace, name='travel-places'),
    path('book-guide/', book_guide_by_location, name='book-guide-by-location'),
    path('update-booking-status/', updateGuideBookingStatus, name='update-booking-status'),
    path('guide-booking-list/', get_guide_booking_list, name='guide_booking_list'),
    path('user-booking-list/', get_user_booking_list, name='user_booking_list'),
    path('report-user/', report_guide, name='report_guide'),
]