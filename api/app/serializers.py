from rest_framework import serializers
from .models import *
from users.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'user_type', 'last_login']

class GuideSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    
    class Meta:
        model = Guide
        fields = ['id', 'user']

class TravelPlaceSerializer(serializers.ModelSerializer):    
    class Meta:
        model = TravelPlace
        fields = ['id', 'name', 'location', 'description']
        
    def create(self, validated_data):
        place = TravelPlace(
            name = validated_data['name'],
            location = validated_data['location'],
            description = validated_data['description']
        )
        
        place.save()

        return place
    
class GuideDetailSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    travel_places = TravelPlaceSerializer(many=True)
    
    class Meta:
        model = Guide
        fields = ['id', 'user', 'travel_places']

class GuideBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookGuide
        fields = ['travel_user', 'guide_user', 'travel_location', 'travel_place', 'booking_date', 'status', 'cancel_reason', 'canceled_by']
        read_only_fields = ['status']  # Status will be set automatically to 'pending'

    # Custom validation to ensure the guide is available for the location
    def validate(self, data):
        guide = data.get('guide')
        location = data.get('travel_location')

        # Check if the guide is available for the location
        if not Guide.objects.filter(user=guide, travel_places__location=location).exists():
            raise serializers.ValidationError(f"The selected guide is not available for the location: {location}")
        
        return data