from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django import forms
from django.contrib.auth.forms import UserCreationForm

# Custom UserCreationForm to handle user_type field
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type')

# Customizing the CustomUserAdmin to show user_type on the add page
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm  # Use the custom form for the Add User page
    model = CustomUser

    # Customize the add_fieldsets to show user_type on the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )

    # Ensure user_type appears in the user detail and list view
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type',)}),
    )
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')

# Register the custom user admin
admin.site.site_title = "TGB Admin portal"
admin.site.site_header = "TGB Admin"
admin.site.register(CustomUser, CustomUserAdmin)