from rest_framework import serializers
from users.models import CustomUser

class CustomUserResitrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'password', 'password2']
        extra_kwargs={
            'password':{'write_only':True}
        }
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        
        if(password != password2):
            raise serializers.ValidationError("Password and Re password are not the same.")
        return attrs

    def create(self, validate_data):
        user = CustomUser(
            username=validate_data['username'],
            email=validate_data['email'],
            user_type=validate_data['user_type'],
        )
        
        user.set_password(validate_data['password'])
        user.save()
        
        return user

class CustomUserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'