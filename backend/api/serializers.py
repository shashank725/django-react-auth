from rest_framework import serializers
# For Password Reset(SendPasswordResetEmailSerializer)
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .models import User
from .utils import Util


class UserRegistrationSerializer(serializers.ModelSerializer):
    #We are writing this because we need confirm password filed in our Registration request
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'name', 'tc', 'password', 'password2']
        extra_kwargs = {
            'password':{'write_only': True}
            }

    #Object level validation
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
    # def validate(self, attrs):         
    #     email = attrs.get('email')
    #     password = attrs.get('password')
    #     user = User.objects.filter(email=email).first()
    #     if user:
    #         if not user.check_password(password):
    #             raise serializers.ValidationError("Password is incorrect")
    #     else:
    #         raise serializers.ValidationError("User does not exist")
    #     return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['password', 'password2']

    def validate(self, attrs):          
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password must be same")
        user.set_password(password)
        user.save()
        return attrs


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    class Meta:
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print("Encoded UID: ", uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print("Password Reset Token: ", token)
            link = 'http://localhost:3000/api/user/reset/' + uid + '/' + token + '/'
            print("Password Reset Link: ", link)
            # Send Email
            data = {
                'subject': 'Password Reset',
                'body': 'Click on the link to reset your password: ' + link,
                'to_email': user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError("User does not exist")


class UserPasswordResetSerilizer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['password', 'password2']

    def validate(self, attrs):        
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password must be same")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationError("Token is Invalid or Expired")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise ValidationError("Token is Invalid or Expired")



