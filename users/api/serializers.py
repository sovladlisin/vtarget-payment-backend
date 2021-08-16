from rest_framework import serializers

from users.models import Account
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self):

        account = Account(
            email=self.validated_data['email'],
            username=self.validated_data['email'] + 'username'
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError(
                {'password': 'Passwords must match.'})
        account.set_password(password)
        account.save()
        return account


class LoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def authenticate(self):

        account = authenticate(
            username=self.validated_data['username'], password=self.validated_data['password'])
        if account is None:
            raise serializers.ValidationError(
                {'password': 'Passwords is incorrect.'})

        return account
