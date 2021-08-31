from django.http.response import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.api.serializers import LoginSerializer, RegistrationSerializer
from rest_framework.authtoken.models import Token

import json

from cabinets.api.client_methods import getVkUserInfo
from users.models import Account, VkProfile

from django.contrib.auth import authenticate


@api_view(['POST', ])
@permission_classes((AllowAny,))
def registration_view(request):

    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data = collect_account_func(account)
        else:
            print('not valis')
            data = serializer.errors
        return Response(data)


@api_view(['POST', ])
@permission_classes((AllowAny,))
def login_view(request):

    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.authenticate()
            data = collect_account_func(account)

        else:
            print('valid error')
            data = serializer.errors
        return Response(data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def change_email_view(request):

    if request.method == 'POST':
        v_data = json.loads(request.body.decode('utf-8'))
        password = v_data.get('password', None)
        new_email = v_data.get('new_email', None)

        if None in [password, new_email]:
            return HttpResponse(status=400)

        data = {}
        account = authenticate(
            username=request.user.email, password=password)
        if account is None:
            return HttpResponse(status=301)

        account.email = new_email
        account.username = new_email + 'username'

        account.save()

        data = collect_account_func(account)

        return Response(data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def change_password_view(request):

    if request.method == 'POST':
        v_data = json.loads(request.body.decode('utf-8'))
        password = v_data.get('password', None)
        new_password = v_data.get('new_password', None)

        if None in [password, new_password]:
            return HttpResponse(status=400)

        data = {}
        account = authenticate(
            username=request.user.email, password=password)
        if account is None:
            return HttpResponse(status=301)

        account.set_password(new_password)

        account.save()

        data = collect_account_func(account)

        return Response(data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def connect_vk_profile(request):
    if request.method == 'POST':
        v_data = json.loads(request.body.decode('utf-8'))
        token = v_data.get('token', None)
        vk_id = v_data.get('vk_id', None)

        if None in [token, vk_id]:
            return HttpResponse(status=400)

        user_info = getVkUserInfo(token, vk_id)
        if user_info == -1:
            return HttpResponse(status=500)

        user = request.user

        existed_profiles = VkProfile.objects.all().filter(user=user)
        if existed_profiles.count() > 0:
            for p in existed_profiles:
                p.delete()

        new_vk_profile = VkProfile(
            user=user, vk_id=vk_id, name=user_info['name'], photo=user_info['photo'], token=token)
        new_vk_profile.save()

        data = {}
        data['name'] = new_vk_profile.name
        data['photo'] = new_vk_profile.photo
        data['vk_id'] = int(new_vk_profile.vk_id)

        return Response(data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def update_account_info(request):
    response = collect_account_func(request.user)
    return Response(response)


def collect_account_func(account):
    data = {}
    data['response'] = 'Success'
    data['email'] = account.email
    data['username'] = account.email
    token = Token.objects.get(user=account).key
    data['token'] = token
    data['is_admin'] = account.is_admin
    data['id'] = account.pk
    data['is_online'] = True
    data['wallet'] = account.wallet

    data['vk_profile'] = None
    vk_profile = VkProfile.objects.all().filter(user=account)
    if vk_profile.count() == 1:
        vk_profile = vk_profile.first()
        vk_profile_data = {}
        vk_profile_data['name'] = vk_profile.name
        vk_profile_data['photo'] = vk_profile.photo
        vk_profile_data['vk_id'] = int(vk_profile.vk_id)
        data['vk_profile'] = vk_profile_data
    return data
