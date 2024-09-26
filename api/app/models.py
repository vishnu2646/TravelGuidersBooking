from django.db import models
from users.models import CustomUser
from django.utils import timezone

# Create your models here.
class TravelPlace(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)  # City or broader location name
    description = models.TextField()
    
    def __str__(self) -> str:
        return self.name
    
    # Method to get all guides for the place
    def get_guides(self):
        return self.guides.all()

class Guide(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        limit_choices_to={'user_type': 'guide'}, 
        on_delete=models.CASCADE
    )
    travel_places = models.ManyToManyField(TravelPlace, related_name='guides')
    
    def __str__(self) -> str:
        return f"{self.user.username} - Guide"
    
class TravelUser(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'travel_user'}
    )
    
    def __str__(self) -> str:
        return f"{self.user.username} - Travel User"

    # Method to get all travel spots for a specific location
    def get_travel_places_for_location(self, location):
        return TravelPlace.objects.filter(location=location)
    
    # Method to get guides associated with a specific travel place
    def get_guides_for_location(self, location):
        travel_places = TravelPlace.objects.filter(location=location)
        return Guide.objects.filter(travel_places__in=travel_places).distinct()

# Note: Add a column that represents who cancelled the booking, either by guide_user or travel_user
class BookGuide(models.Model):
    travel_user = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        limit_choices_to={'user_type': 'travel_user'},
        related_name='bookings_as_travel_user'
    )
    guide_user = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        limit_choices_to={'user_type': 'guide'},
        related_name='bookings_as_guide',
        null=True, blank=True  # Nullable in case guide is assigned later
    )
    travel_location = models.CharField(max_length=255)  # Location is chosen for booking
    travel_place = models.ForeignKey(
        TravelPlace, 
        on_delete=models.PROTECT, 
        null=True, blank=True  # Nullable in case place is assigned later
    )
    booking_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=50, 
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], 
        default='pending'
    )
    cancel_reason = models.TextField(blank=True, null=True)
    canceled_by = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.PROTECT)
    
    def __str__(self) -> str:
        return f"Booking by {self.travel_user.username} for {self.travel_location}"
    
    # Optional: Method to assign a guide after location is selected
    def assign_guide(self, guide):
        if guide in Guide.objects.filter(travel_places__location=self.travel_location).distinct():
            self.guide = guide
            self.save()

    # Optional: Method to assign a travel place
    def assign_travel_place(self, travel_place):
        if travel_place.location == self.travel_location:
            self.travel_place = travel_place
            self.save()
