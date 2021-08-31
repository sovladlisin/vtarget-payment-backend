from django.http import response
from django.http.response import HttpResponse
from cabinets.api.client_methods import getClient, updateClient
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.api.serializers import LoginSerializer, RegistrationSerializer
from rest_framework.authtoken.models import Token

import json

from users.models import Account, VkProfile
from cabinets.models import AccountPermission, ClientUser, Payment

import time
import requests
import hashlib
import datetime

from django.forms.models import model_to_dict

token = 'd8b388a3fe42057a5fadf69b545658b41fb9a2fc1579dbc6fe6a965e74f8e27689428ccbdc79415af1a9c'
account_id = 1900015024


terminal = '1624995550332DEMO'
terminal_password = 'e4u79jezxgn7c7po'


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def start_payment_process(request):

    if request.method == 'POST':

        v_data = json.loads(request.body.decode('utf-8'))
        user = request.user
        amount = v_data.get('amount', None)
        is_wallet = v_data.get('is_wallet', None)
        client_id = v_data.get('client_id', None)
        email = v_data.get('email', None)

        if None in [amount, is_wallet, client_id, email]:
            return HttpResponse(status=400)

        if amount == 0 or is_wallet not in [0, 1]:
            return HttpResponse(status=400)

        # payments = Payment.objects.all().filter(user=user, amount=amount, is_wallet=is_wallet, terminal_key=terminal)
        # if payments.count() != 0:
        #     existing_payment = payment

        bank_request_params = {}
        bank_request_params['TerminalKey'] = terminal
        bank_request_params['Amount'] = amount * 100

        order_id = "{is_wallet}_{client_id}_{user_pk}_{amount}_{time}".format(
            is_wallet=is_wallet, client_id=client_id, user_pk=user.pk, time=int(time.time()), amount=amount)

        bank_request_params['OrderId'] = order_id
        bank_request_params['Description'] = 'Desc'

        # generating payment token
        bank_request_params['Token'] = get_request_token(bank_request_params)

        bank_request_params['Receipt'] = {
            'Email': email,
            'Taxation': 'osn',
            'Items': [{
                'Tax': 'none',
                'Name': 'Пополнение эл. счета' if is_wallet == 1 else ('Пополнение кабинета №' + str(client_id)),
                'Quantity': 1,
                'Amount': amount * 100,
                'Price': amount * 100,
                'PaymentObject': 'payment'
            }]
        }

        headers = {'Content-type': 'application/json'}
        bank_response = requests.post(
            'https://securepay.tinkoff.ru/v2/Init', data=json.dumps(bank_request_params), headers=headers)
        bank_response_obj = bank_response.json()
        print(bank_response_obj)
        new_payment = Payment(
            status=bank_response_obj['Status'],
            terminal_key=bank_response_obj['TerminalKey'],
            payment_id=bank_response_obj['PaymentId'],
            order_id=bank_response_obj['OrderId'],
            amount=int(bank_response_obj['Amount']) / 100,
            payment_url=bank_response_obj['PaymentURL'],
            is_wallet=is_wallet,
            user=user,
            date=datetime.datetime.now()
        )

        new_payment.save()
        return Response(model_to_dict(new_payment))


@api_view(['POST', ])
@permission_classes((AllowAny,))
def update_payment_details(request):
    # print(request.REMOTE_HOST)

    if request.method == 'POST':

        v_data = json.loads(request.body.decode('utf-8'))
        print(v_data)
        status = v_data.get('Status', None)
        order_id = v_data.get('OrderId', None)

        payment = Payment.objects.all().filter(order_id=order_id)
        if payment.count() != 1:
            return HttpResponse('OK', content_type="text/plain", status=200)

        payment = payment.first()

        # CONFIRMED

        if status in ['CONFIRMED'] and not payment.is_processed:
            if payment.is_wallet == 0:
                order_data = order_id.split('_')
                client_id = int(order_data[1])
                client_data = getClient(account_id, token, client_id)

                all_limit = int(client_data['all_limit'])
                all_limit += payment.amount

                response = updateClient(
                    account_id, token, client_id, client_data['name'], client_data['day_limit'], all_limit)
                if response == -1:
                    return HttpResponse(status=500)
                payment.is_processed = True
                payment.save()
            else:
                user = payment.user
                user.wallet = user.wallet + payment.amount
                user.save()
                payment.is_processed = True
                payment.save()

        if status in ['CANCELED', 'REFUNDED']:

            if payment.is_processed and not payment.is_refunded:

                if payment.is_wallet == 0:
                    order_data = order_id.split('_')
                    client_id = int(order_data[1])
                    client_data = getClient(account_id, token, client_id)

                    all_limit = int(client_data['all_limit'])
                    all_limit -= payment.amount

                    response = updateClient(
                        account_id, token, client_id, client_data['name'], client_data['day_limit'], all_limit)
                    if response == -1:
                        return HttpResponse(status=500)
                    payment.is_refunded = True
                else:
                    user = payment.user
                    user.wallet = user.wallet - payment.amount
                    user.save()
                    payment.is_refunded = True
            else:
                payment.is_refunded = True

        payment.status = status
        payment.save()
        return HttpResponse('OK', content_type="text/plain", status=200)
        # {
        #     "Success": true,
        #     "ErrorCode": "0",
        #     "TerminalKey": "TinkoffBankTest",
        #     "Status": "NEW",
        #     "PaymentId": "13660",
        #     "OrderId": "21050",
        #     "Amount": 100000,
        #     "PaymentURL": "https://securepay.tinkoff.ru/rest/Authorize/1B63Y1"
        # }


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_payments(request):

    if request.method == 'GET':
        user = request.user
        payments = Payment.objects.all().filter(user=user)

        response = []
        for payment in payments:
            response.append(model_to_dict(payment))
        return Response(response)
    return HttpResponse(status=403)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def refund_payment(request):

    if request.method == 'POST':
        user = request.user

        v_data = json.loads(request.body.decode('utf-8'))
        order_id = v_data.get('order_id', None)
        if None in [order_id]:
            return HttpResponse(status=400)

        payment = Payment.objects.all().filter(order_id=order_id)
        if payment.count() != 1:
            return HttpResponse(status=400)

        payment = payment.first()

        if payment.user != user:
            return HttpResponse(status=403)

        bank_request_params = {
            "TerminalKey": terminal,
            "PaymentId": payment.payment_id,
        }
        bank_request_params['Token'] = get_request_token(bank_request_params)

        headers = {'Content-type': 'application/json'}
        bank_response = requests.post(
            'https://securepay.tinkoff.ru/v2/Cancel', data=json.dumps(bank_request_params), headers=headers)
        bank_response_obj = bank_response.json()

        if payment.is_processed and not payment.is_refunded:

            if payment.is_wallet == 0:
                order_data = bank_response_obj['OrderId'].split('_')
                client_id = int(order_data[1])
                client_data = getClient(account_id, token, client_id)

                all_limit = int(client_data['all_limit'])
                all_limit -= payment.amount

                response = updateClient(
                    account_id, token, client_id, client_data['name'], client_data['day_limit'], all_limit)
                if response == -1:
                    return HttpResponse(status=500)
                payment.is_refunded = True
            else:
                user = payment.user
                user.wallet = user.wallet - payment.amount
                user.save()
                payment.is_refunded = True
        else:
            payment.is_refunded = True

        payment.status = bank_response_obj['Status']
        payment.save()

        response = model_to_dict(payment)

        return Response(response)
    return HttpResponse(status=403)


def get_request_token(params):
    params['Password'] = terminal_password
    collected_string = ''
    for key in sorted(params.keys()):
        collected_string += str(params[key])
    hash_object = hashlib.sha256(collected_string.encode())
    return hash_object.hexdigest()


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def transfer_with_wallet(request):
    if request.method == 'POST':
        user = request.user
        v_data = json.loads(request.body.decode('utf-8'))
        is_adding = v_data.get('is_adding', None)
        client_id = v_data.get('client_id', None)
        amount = v_data.get('amount', None)

        if None in [is_adding, client_id, amount]:
            return HttpResponse('Неправильные входные параметры', status=400)

        amount = int(amount)

        if is_adding == 1:
            client_data = getClient(account_id, token, client_id)
            all_limit = int(client_data['all_limit'])
            all_limit -= amount
            if all_limit < 0:
                return HttpResponse('Недостаточно средств', status=400)

            response = updateClient(
                account_id, token, client_id, client_data['name'], client_data['day_limit'], all_limit)

            if response == -1:
                return HttpResponse(status=500)

            user.wallet += amount
            user.save()

            return HttpResponse(status=200)

        if is_adding == 0:
            client_data = getClient(account_id, token, client_id)
            all_limit = int(client_data['all_limit'])
            all_limit += amount

            if user.wallet - amount < 0:
                return HttpResponse('Недостаточно средств', status=400)

            response = updateClient(
                account_id, token, client_id, client_data['name'], client_data['day_limit'], all_limit)

            if response == -1:
                return HttpResponse(status=500)

            user.wallet -= amount
            user.save()

            return HttpResponse(status=200)

    return HttpResponse(status=403)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def transfer_with_clients(request):
    if request.method == 'POST':
        user = request.user
        v_data = json.loads(request.body.decode('utf-8'))
        client_id_from = v_data.get('client_id', None)
        client_id_to = v_data.get('client_id', None)
        amount = v_data.get('amount', None)

        if None in [client_id_from, client_id_to, amount]:
            return HttpResponse('Неправильные входные параметры', status=400)

        amount = int(amount)

        client_data_from = getClient(account_id, token, client_id_from)
        client_data_to = getClient(account_id, token, client_id_to)

        all_limit_from = int(client_data_from['all_limit'])
        all_limit_to = int(client_data_to['all_limit'])

        if all_limit_from - amount < 0:
            return HttpResponse('Недостаточно средств', status=400)

        all_limit_from -= amount
        all_limit_to += amount

        response_from = updateClient(
            account_id, token, client_id_from, client_id_from['name'], client_id_from['day_limit'], all_limit_from)
        response_to = updateClient(
            account_id, token, client_data_to, client_data_to['name'], client_data_to['day_limit'], all_limit_to)
        if response_from == -1 or response_to == -1:
            return HttpResponse(status=500)

        return HttpResponse(status=200)

    return HttpResponse(status=403)
