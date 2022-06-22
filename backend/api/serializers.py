from pyexpat import model
from rest_framework import serializers

from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    #We are writing this because we need confirm password filed in our Registration request
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'name', 'tc', 'password', 'password2']
        extra_kwargs = {
            'password':{'write_only': True}
            }

    # Validate password and confrim password while Registration
    def validate(self, attrs):           #attrs (variable) is a dictionary of all the fields in the request
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password must be same")
        return attrs
    
    # Create user while Registration (We are using this because we are using Custom User Model)
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']

    # # Validate password while Login
    # def validate(self, attrs):           #attrs (variable) is a dictionary of all the fields in the request
    #     email = attrs.get('email')
    #     password = attrs.get('password')
    #     user = User.objects.filter(email=email).first()
    #     if user:
    #         if not user.check_password(password):
    #             raise serializers.ValidationError("Password is incorrect")
    #     else:
    #         raise serializers.ValidationError("User does not exist")
    #     return attrs