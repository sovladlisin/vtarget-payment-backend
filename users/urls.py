from django.urls import path
from .views import getAllUsers, login

# urlpatterns = [path('api/vkUserPermissions',
#                     getPermissions, name='vkUserPermissions')]
urlpatterns = [
    path('login',
         login, name='login'),
    path('getAllUsers',
         getAllUsers, name='getAllUsers'),
]
