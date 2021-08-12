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


@api_view(['POST', ])
@permission_classes((AllowAny,))
def registration_view(request):

    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = 'Success'
            data['email'] = account.email
            data['username'] = account.username
            token = Token.objects.get(user=account).key
            data['token'] = token
            data['is_admin'] = account.is_admin
            data['id'] = account.pk
            data['is_online'] = True

            data['vk_profile'] = None
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
            data['response'] = 'Success'
            data['email'] = account.email
            data['username'] = account.username
            token = Token.objects.get(user=account).key
            data['token'] = token
            data['is_admin'] = account.is_admin
            data['id'] = account.pk
            data['is_online'] = True

            data['vk_profile'] = None
            vk_profile = VkProfile.objects.all().filter(user=account)
            if vk_profile.count() == 1:
                vk_profile = vk_profile.first()
                vk_profile_data = {}
                vk_profile_data['name'] = vk_profile.name
                vk_profile_data['photo'] = vk_profile.photo
                vk_profile_data['vk_id'] = int(vk_profile.vk_id)
                data['vk_profile'] = vk_profile_data

        else:
            data = serializer.errors
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
