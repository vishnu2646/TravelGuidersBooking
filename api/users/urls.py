from django.urls import path
from users.views import *

urlpatterns = [
    path('', home, name='home'),
    path('sign-up', registerUser, name='sign-up'),
    path('sign-in', loginUser, name='sign-in'),
    path('profile/<str:username>', getUserProfile, name='profile'),
    path('profile/<str:username>/update', updateUserProfile, name='profile-update'),
]