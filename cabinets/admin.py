from django.contrib import admin

from .models import Payment
# Register your models here.


class PaymentAdmin(admin.ModelAdmin):
    model = Payment


admin.site.register(Payment, PaymentAdmin)
