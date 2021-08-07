from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from .models import VkUser
from cabinets.views import vk_request
import requests
# import jwt
from django.contrib.auth import authenticate

# client_id = '7613764'
client_id = '7647441'

# client_secret = 'B9MxUsRKbMNCWwvJgIPM'
client_secret = 'ClAXUPylS1FBGWxw6y2n'

KEY = 'hfslakwjhbkjgnwvfejwnoguihqwivfuh3qwrnoiuhwneot36qwooiwehiuqhrowrgwaaa'


@csrf_exempt
def login(request):
    if request.method == 'POST':
        user = json.loads(request.body.decode('utf-8'))
        user_id = user.get('user_id', None)
        token = user.get('access_token', None)
        if token is not None:

            users = VkUser.objects.all().filter(user_id=user_id)
            if not users:
                user_data = vk_request('get', 'users.get', {
                                       'user_ids': user_id, 'fields': 'photo_200'}, token, '5.124')['response'][0]
                new_user = VkUser(
                    user_id=user_data['id'], user_img=user_data['photo_200'], user_name=user_data['first_name'] + ' ' + user_data['last_name'], token=token, post_token='')
                new_user.save()
                # new_user.token = True
                result = model_to_dict(new_user)
                return JsonResponse(result, safe=False)
            else:
                old_user = users.first()
                old_user.token = token
                old_user.save()
                # old_user.token = True
                result = model_to_dict(old_user)
                return JsonResponse(result, safe=False)
    return HttpResponse('Wrong request')


@csrf_exempt
def getAllUsers(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        admin_pk = data.get('admin_pk', None)
        admin = VkUser.objects.get(pk=admin_pk)
        if admin.is_admin is False:
            return HttpResponse(status=403)

        result = []
        for user in VkUser.objects.all():
            temp = model_to_dict(user)
            temp['token'] = ''
            temp['post_token'] = ''
            temp['shutterstock_token'] = ''
            temp['medals'] = json.loads(user.medals)
            result.append(temp)

        return JsonResponse(result, safe=False)
    return HttpResponse('Wrong request')

# def authenticate_user(token):
#     if len(token) == 0:
#         return None
#     print(token)
#     user_dict = jwt.decode(token, KEY, algorithms=["HS256"])
#     username = user_dict.get('username', None)
#     password = user_dict.get('password', None)
#     user = authenticate(username=username, password=password)
#     if user is None:
#         return None
#     user_info = UserInfo.objects.filter(user=user).first()
#     return user_info
