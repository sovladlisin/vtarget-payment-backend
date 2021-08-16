from django.urls import path
from users.api.views import(
    registration_view,
    login_view,
    connect_vk_profile,
    change_email_view,
    change_password_view
)

from rest_framework.authtoken.views import obtain_auth_token

# app_name = 'users'

urlpatterns = [
    path('register', registration_view, name="register"),
    # -> see accounts/api/views.py for response and url info
    path('login', login_view, name="login"),
    path('connectVkProfile', connect_vk_profile, name="connectVK"),
    path('changeEmailCredentials', change_email_view,
         name="changeEmailCredentials"),
    path('changePasswordCredentials', change_password_view,
         name="changePasswordCredentials"),
]
