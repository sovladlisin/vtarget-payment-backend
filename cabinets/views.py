from django.shortcuts import render
import requests
import json
from django.shortcuts import render
from datetime import date, datetime, timedelta
from json.decoder import JSONDecodeError
from dateutil.relativedelta import relativedelta
import datetime as dt
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse
import json
from django.http import StreamingHttpResponse, HttpResponseRedirect, HttpResponse

import string
import random


def vk_request(type, name, params, token, v):
    params['access_token'] = token
    params['v'] = v

    if type == 'get':
        r = requests.get('https://api.vk.com/method/' + name, params)
        return r.json()
    if type == 'post':
        r = requests.post('https://api.vk.com/method/' + name, params)
        return r.json()


@csrf_exempt
def getAccountCabinets(request):
    token = '72d21f0cf9b7538f3aeb5965cfd92db4150c0fef0ebe0766284f5631e6b96ad1839198771eddf8a0dd63e'

    r = vk_request('get', 'ads.getAccounts', {}, token, '5.131')

    accounts = r['response']
    response = []
    for account in accounts:
        id = account['account_id']
        name = account['account_name']
        status = account['account_status']
        account_type = account['account_type']
        can_view_budget = account['can_view_budget']

        stat_request = vk_request('get', 'ads.getStatistics', {
                                  'account_id': id, 'ids_type': 'office', 'ids': id, 'period': 'overall', 'date_from': '0', 'date_to': '0'}, token, '5.131')

        spent = 0
        if stat_request.get('response', None) is not None:
            spent = stat_request['response'][0]['stats'][0]['spent']
    new_account = {}
    new_account['id'] = id
    new_account['name'] = name
    new_account['status'] = status
    new_account['account_type'] = account_type
    new_account['account_type'] = account_type

# @csrf_exempt
# def createClientCabinet(request):
#     data = json.loads(request.body.decode('utf-8'))
#     client_name = data.get('client_name', None)
#     client_user_permissions = data.get('client_name', None)
#     account_id = data.get('account_id', None)
#     day_limit = data.get('day_limit', None)
#     all_limit = data.get('all_limit', None)

#     if client_name is None or client_user_permissions is None or account_id is None or day_limit is None or all_limit is None:
#         return HttpResponse(status=400)


#     create_params = {'account_id':account_id, 'data': json.dumps([{'name': client_name, 'day_limit': day_limit, 'all_limit': 1}]) }
#     create_request = 
