from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
  
@api_view(['GET'])
def home(request):
    return Response({ "message": "Welcome to users" })

@api_view(['POST'])
def registerUser(request):
    if request.method == 'POST':
        serializer = CustomUserResitrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({ "message": "user created successfully 😊", "token": token }, status=status.HTTP_201_CREATED)
        else:
            return Response({ "message": "something went wrong... 😟" ,"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST'])
def loginUser(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
                
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            update_last_login(None, user)
            token = get_tokens_for_user(user)
            return Response({ "message": "Login successfully done", "token": token }, status=status.HTTP_200_OK)
        else:
            return Response({ "message": "Invalied username or password" }, status=status.HTTP_400_BAD_REQUEST)
    return Response("something went error", status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request, username):
    try:
        # Fetch the authenticated user (who should match the token)
        if request.user.username != username:
            return Response({ "message": "You can only update your own profile." }, status=status.HTTP_403_FORBIDDEN)
        
        user = CustomUser.objects.get(username=username)
        
        serializer = CustomUserProfileUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({ "message": "Profile has been updated" }, status=status.HTTP_200_OK)
        else:     
            return Response({ "message": "Invalid Profile data", "errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
        
    except CustomUser.DoesNotExist:
        return Response({ "message": "User not found" }, status=status.HTTP_404_NOT_FOUND)
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request, username):
    try:
        # Fetch the authenticated user (who should match the token)
        if request.user.username != username:
            return Response({ "message": "You can only update your own profile." }, status=status.HTTP_403_FORBIDDEN)
        
        user = CustomUser.objects.get(username=username)
        data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_type": user.user_type,
            "phone": user.phone
        }
        if user is not None:
            return Response({ "message": "user data", "data": data }, status=status.HTTP_200_OK)
        else:
            return Response({ "message": "user not found", "data": {} }, status=status.HTTP_404_NOT_FOUND)
    except CustomUser.DoesNotExist:
        return Response({ "message": "User not found" }, status=status.HTTP_404_NOT_FOUND)
