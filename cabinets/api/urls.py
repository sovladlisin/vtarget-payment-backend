from django.urls import path
from cabinets.api.views import(
    get_vk_user_info,
    create_client,
    delete_client,
    update_client_meta,
    update_client_permissions,
    get_client_list
)
from cabinets.api.payment import (
    start_payment_process,
    update_payment_details,
    get_payments,
    refund_payment,
    transfer_with_wallet,
    transfer_with_clients
)

from rest_framework.authtoken.views import obtain_auth_token

# app_name = 'users'

urlpatterns = [
    path('getVkUserInfo', get_vk_user_info, name="getVkUserInfo"),

    path('getClients', get_client_list, name="getClients"),
    path('createClient', create_client, name="createClient"),
    path('deleteClient', delete_client, name="deleteClient"),
    path('updateClientMeta', update_client_meta, name="updateClientMeta"),
    path('updateClientPermissions', update_client_permissions,
         name="updateClientPermissions"),

    # pay
    path('initPayment', start_payment_process,
         name="initPayment"),
    path('updatePayment', update_payment_details,
         name="updatePayment"),
    path('getPayments', get_payments,
         name="getPayments"),
    path('refundPayment', refund_payment,
         name="refundPayment"),
    path('transferWithWallet', transfer_with_wallet,
         name="transferWithWallet"),
    path('transferWithClients', transfer_with_clients,
         name="transferWithClients"),
]
