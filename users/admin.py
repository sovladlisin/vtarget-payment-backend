from django.contrib import admin
from .models import VkUser
# Register your models here.


class VkUserAdmin(admin.ModelAdmin):
    model = VkUser


admin.site.register(VkUser, VkUserAdmin)
