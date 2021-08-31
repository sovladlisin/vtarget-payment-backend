from django.http.response import HttpResponse
from cabinets.api.client_methods import deleteClient, getClients, getVkUserInfo, createClient, updateClient, updateOfficeUsers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.api.serializers import LoginSerializer, RegistrationSerializer
from rest_framework.authtoken.models import Token

import json

from users.models import Account, VkProfile
from cabinets.models import AccountPermission, ClientUser

token = 'd8b388a3fe42057a5fadf69b545658b41fb9a2fc1579dbc6fe6a965e74f8e27689428ccbdc79415af1a9c'
account_id = 1900015024


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def get_vk_user_info(request):

    if request.method == 'POST':

        v_data = json.loads(request.body.decode('utf-8'))
        user_id = v_data.get('user_id', None)
        if user_id is not None:
            data = getVkUserInfo(token, user_id)
            data['response'] = 'Success'
            return Response(data)
        else:
            return HttpResponse(status=400)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_client_list(request):

    if request.method == 'GET':
        user = request.user
        vk_profile = VkProfile.objects.get(user=user)

        client_user = ClientUser.objects.all().filter(vk_id=vk_profile.vk_id)
        if client_user.count() == 0:
            client_user = ClientUser(
                vk_id=vk_profile.vk_id, name=vk_profile.name, photo=vk_profile.photo)
            client_user.save()
        else:
            client_user = client_user.first()
        clients = getClients(account_id, token)
        if clients == -1:
            return HttpResponse(status=500)

        data = []
        for client in clients:
            security_check = False

            client_data = {}
            perms = AccountPermission.objects.all().filter(
                client_id=client['id'])

            perms_list = []
            for perm in perms:
                security_check = True if perm.user == client_user else security_check

                perms_data = {}
                perms_data['photo'] = perm.user.photo
                perms_data['name'] = perm.user.name
                perms_data['vk_id'] = perm.user.vk_id
                perms_data['role'] = perm.role
                perms_list.append(perms_data)

            client_data['client_users'] = perms_list
            client_data['id'] = client['id']
            client_data['spent'] = client['spent']
            client_data['name'] = client['name']
            client_data['account_id'] = account_id
            client_data['day_limit'] = int(client['day_limit'])
            client_data['all_limit'] = int(client['all_limit'])

            # in dev
            client_data['balance'] = 1000
            client_data['status'] = 1

            if security_check:
                data.append(client_data)

        return Response(data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def create_client(request):
    if request.method == 'POST':
        v_data = json.loads(request.body.decode('utf-8'))
        name = v_data.get('name', None)
        day_limit = v_data.get('day_limit', None)
        all_limit = v_data.get('all_limit', None)
        user = request.user

        if None in [day_limit, name, all_limit]:
            return HttpResponse(status=400)

        created_client_id = createClient(
            account_id, token, name, day_limit, all_limit)
        if created_client_id == -1:
            return HttpResponse(status=500)

        vk_profile = VkProfile.objects.get(user=user)

        # creating permissions on vk side
        updateOfficeUsers(token, account_id,
                          created_client_id, [vk_profile.vk_id])

        client_user = ClientUser.objects.all().filter(vk_id=vk_profile.vk_id)

        if client_user.count() == 1:
            client_user = client_user.first()
        else:
            client_user = ClientUser(
                vk_id=vk_profile.vk_id, name=vk_profile.name, photo=vk_profile.photo)
            client_user.save()

        creator_permission = AccountPermission(
            user=client_user, role=2, client_id=created_client_id)
        creator_permission.save()

        data = {}
        data['client_users'] = [{'role': 2, 'name': client_user.name,
                                 'photo': client_user.photo, 'vk_id': client_user.vk_id}]
        data['id'] = created_client_id
        data['spent'] = 0
        data['balance'] = 0
        data['name'] = name
        data['account_id'] = account_id
        data['day_limit'] = int(day_limit)
        data['all_limit'] = int(all_limit)

        return Response(data)


@api_view(['DELETE', ])
@permission_classes((IsAuthenticated,))
def delete_client(request):
    if request.method == 'DELETE':
        client_id = request.GET.get('id', None)

        if client_id is None:
            return HttpResponse(status=400)

        user = request.user
        vk_profile = VkProfile.objects.get(user=user)
        client_user = ClientUser.objects.get(vk_id=vk_profile.vk_id)

        perm = AccountPermission.objects.all().filter(
            client_id=client_id, user=client_user)
        if perm.count() == 1:
            perm = perm.first()
            if perm.role == 2:
                deleted = deleteClient(account_id, token, client_id)
                if deleted in [0, 600]:
                    for p in AccountPermission.objects.all().filter(client_id=client_id):
                        p.delete()

                        # removing permissions on vk side
                        updateOfficeUsers(token, account_id, client_id, [])

                    return HttpResponse(status=200)
                else:
                    return HttpResponse(status=500)
            else:
                return HttpResponse(status=301)
        else:
            return HttpResponse(status=301)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def update_client_meta(request):
    if request.method == 'POST':
        user = request.user
        v_data = json.loads(request.body.decode('utf-8'))

        client_id = v_data.get('id', None)
        name = v_data.get('name', None)
        day_limit = v_data.get('day_limit', None)
        all_limit = v_data.get('all_limit', None)

        if None in [client_id, name, day_limit, all_limit]:
            return HttpResponse(status=400)

        vk_profile = VkProfile.objects.get(user=user)
        client_user = ClientUser.objects.get(vk_id=vk_profile.vk_id)

        account_perm = AccountPermission.objects.all().filter(
            user=client_user, client_id=client_id)

        if account_perm.count() == 1:
            account_perm = account_perm.first()
            if account_perm.role == 2:

                updated_client_id = updateClient(
                    account_id, token, client_id, name, day_limit, all_limit)

                if updated_client_id == -1:
                    return HttpResponse(status=500)

                return HttpResponse(status=200)

            else:
                return HttpResponse(status=301)
        else:
            return HttpResponse(status=301)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def update_client_permissions(request):
    if request.method == 'POST':
        user = request.user
        v_data = json.loads(request.body.decode('utf-8'))
        client_id = v_data.get('id', None)
        new_permissions = v_data.get('permissions', None)
        if None in [client_id, new_permissions]:
            return HttpResponse(status=400)

        vk_profile = VkProfile.objects.get(user=user)
        client_user = ClientUser.objects.get(vk_id=vk_profile.vk_id)

        account_perm = AccountPermission.objects.all().filter(
            user=client_user, client_id=client_id)
        if account_perm.count() == 1:
            account_perm = account_perm.first()
            if account_perm.role in [1, 2]:
                for old_perm in AccountPermission.objects.all().filter(client_id=client_id).exclude(role=2):
                    old_perm.delete()

                # client ids for vk
                vk_client_ids = []
                for new_perm in new_permissions:
                    if new_perm['role'] != 2:
                        new_client_user = ClientUser.objects.all().filter(
                            vk_id=new_perm['vk_id'])
                        if new_client_user.count() == 1:
                            new_client_user = new_client_user.first()
                        else:
                            new_client_user = ClientUser(
                                vk_id=new_perm['vk_id'], name=new_perm['name'], photo=new_perm['photo'])
                            new_client_user.save()
                        new_account_permission = AccountPermission(
                            user=new_client_user, role=new_perm['role'], client_id=client_id)
                        new_account_permission.save()

                    vk_client_ids.append(new_perm['vk_id'])

                updateOfficeUsers(token, account_id, client_id, vk_client_ids)
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=301)
        return HttpResponse(status=301)
