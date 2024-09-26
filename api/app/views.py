from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .decrators import user_type_required
from django.utils import timezone
# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_type_required('travel_user')
def getGuidersByLocation(request):
    location = request.query_params.get('location', None)

    # Filter travel places by location
    if location:
        travel_places = TravelPlace.objects.filter(location__icontains=location)
    else:
        travel_places = TravelPlace.objects.all()

    # Serialize travel places
    places_serializer = TravelPlaceSerializer(travel_places, many=True)
    
    guides = Guide.objects.filter(travel_places__in=travel_places).distinct()
    
    guides_serializer = GuideSerializer(guides, many=True)

    # Combine places and guides into a custom response
    response_data = {
        "places": places_serializer.data,
        "guides": guides_serializer.data
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getGuidersByLocationAndName(request):
    name = request.query_params.get('name', None)
    
    if name:
        place = TravelPlace.objects.filter(name__icontains=name)
    else:
        place = {}
        
    # Serialize travel places
    places_serializer = TravelPlaceSerializer(place, many=True)
    
    guides = Guide.objects.filter(travel_places__in=place).distinct()
    
    guides_serializer = GuideSerializer(guides, many=True)

    # Combine places and guides into a custom response
    response_data = {
        "places": places_serializer.data,
        "guides": guides_serializer.data
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllGuides(request):
    guiders = Guide.objects.all()
    serializer = GuideSerializer(guiders, many=True)
    return Response({ "message": "Guiders", "guiders": serializer.data }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createTravelPlace(request):
    if request.user.user_type != 'admin':
        return Response({ "message": "Travel places can be added by the admin users." })
    
    serializer = TravelPlaceSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({ "message": "Travel Place created Successfully" })
    
    return Response({ "message": "Something went wrong" }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllTravelPlace(request):
    places = TravelPlace.objects.all()
    serializer = TravelPlaceSerializer(places, many=True)
    return Response({ "message": "All Travel Places", "places": serializer.data }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_type_required('travel_user')
def getGuideDetails(request, id):
    # guide_id = request.query_params.get("guide_id")
    guide = Guide.objects.get(id=id)
    serializer = GuideDetailSerializer(guide)
    return Response({ "message": "Guide Details", "guide": serializer.data }, status=status.HTTP_200_OK)

@api_view(['POST'])
@user_type_required('travel_user')
def book_guide_by_location(request):
    travel_user_id = request.data.get('travel_user')
    guide_id = request.data.get('guide_user')
    location = request.data.get('location')
    travel_place_id = request.data.get('travel_place', None)
    booking_date = request.data.get('booking_date', timezone.now())

    guide = Guide.objects.get(id=guide_id)
    guide_serializer = GuideSerializer(guide)
    guide_user_data = guide_serializer.data['user']
    
    try:
        # Fetch travel user and guide objects
        travel_user = CustomUser.objects.get(id=travel_user_id, user_type='travel_user')
        guide_user = CustomUser.objects.get(id=guide_user_data['id'], user_type='guide')
        
        travel_place = None
        if travel_place_id:
            travel_place = TravelPlace.objects.get(id=travel_place_id, location=location)
            
        existing_booking = BookGuide.objects.filter(travel_user=travel_user, guide_user=guide_user, travel_place=travel_place).exclude(status='cancelled').exists()
    
        if existing_booking:
            return Response({ "mesage": "You have alredy booked and the booking is in pending or confirmed status." })
            
        BookGuide.objects.create(
            travel_user=travel_user,
            guide_user=guide_user,
            travel_location=location,
            travel_place=travel_place,
            booking_date=booking_date,
            status="pending"
        )
        
        return Response({"message": f"{guide_user.username} has been booked successfully"}, status=status.HTTP_201_CREATED)
    except CustomUser.DoesNotExist:
        return Response({"error": "Travel user or guide does not exist."}, status=status.HTTP_404_NOT_FOUND)
    except TravelPlace.DoesNotExist:
        return Response({"error": f"Travel place does not exist for the location: {location}"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": "some error occurred", "message": e }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@user_type_required('guide')
def updateGuideBookingStatus(request):
    # Extract booking ID and status from the request data using get method
    booking_id = request.data.get('bookingId')  # Use get() to safely access keys
    new_status = request.data.get('status')     # Use get() to safely access keys
    cancel_reason = request.data.get('cancel_reason')
    # Check if both bookingId and status are provided
    if not booking_id or not new_status:
        return Response({"error": "Booking ID and status are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the booking object
        booking_data = BookGuide.objects.get(id=booking_id)
        # Check if the guide in the booking matches the guide making the request
        if booking_data.guide_user != request.user:
            return Response({"error": "You are not authorized to update this booking"}, status=status.HTTP_403_FORBIDDEN)

        # Update the status based on the request
        if new_status == "confirmed":
            booking_data.status = 'confirmed'
            booking_data.save()
            return Response({"message": "Booking has been confirmed"}, status=status.HTTP_200_OK)
        
        elif new_status == "canceled":
            booking_data.status = 'cancelled'
            booking_data.canceled_by = request.user
            booking_data.cancel_reason = cancel_reason
            booking_data.save()
            return Response({"message": "Booking has been canceled by the guide"}, status=status.HTTP_200_OK)
        
        else:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
    
    except BookGuide.DoesNotExist:
        return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@user_type_required('guide')
def get_guide_booking_list(request):    
    guide_user = request.user
    bookings = BookGuide.objects.filter(guide_user=guide_user) 
    serializer = GuideBookingSerializer(bookings, many=True)
    return Response({"message": "Successfully got the bookings", "data": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@user_type_required('travel_user')
def get_user_booking_list(request):
    travel_user = request.user
    bookings = BookGuide.objects.filter(travel_user=travel_user)
    serializer = GuideBookingSerializer(bookings, many=True)
    return Response({"message": "Successfully got the booking lists", "data": serializer.data }, status=status.HTTP_200_OK)

@api_view(['POST'])
@user_type_required('travel_user')
def cancel_booking_by_travel_user(request):
    # Extract booking ID and status from the request data using get method
    booking_id = request.data.get('bookingId')  # Use get() to safely access keys
    new_status = request.data.get('status')     # Use get() to safely access keys
    cancel_reason = request.data.get('cancel_reason')
    # Check if both bookingId and status are provided
    if not booking_id or not new_status:
        return Response({"error": "Booking ID and status are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the booking object
        booking_data = BookGuide.objects.get(id=booking_id)
        # Check if the guide in the booking matches the guide making the request
        if booking_data.travel_user != request.user:
            return Response({"error": "You are not authorized to update this booking"}, status=status.HTTP_403_FORBIDDEN)

        # Cancel the booking for guide and travel_location
        if new_status == "canceled":
            booking_data.status = 'cancelled'
            booking_data.canceled_by = request.user
            booking_data.cancel_reason = cancel_reason
            booking_data.save()
            return Response({"message": "Booking has been canceled by the guide"}, status=status.HTTP_200_OK)
        
        else:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
    
    except BookGuide.DoesNotExist:
        return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)