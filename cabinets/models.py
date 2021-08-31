from django.db import models
from django.db.models.fields import IntegerField
from users.models import Account
# Create your models here.

# 0 - Наблюдатель
# 1 - Менеджер
# 2 - Создатель


class ClientUser(models.Model):
    name = models.CharField(default='Не указано', max_length=300)
    photo = models.TextField(default='')
    vk_id = models.IntegerField(default=-1, unique=True)


class AccountPermission(models.Model):
    user = models.ForeignKey(
        ClientUser, blank=False, null=False, related_name='permission_actor', on_delete=models.CASCADE)
    role = IntegerField(default=0)
    client_id = IntegerField(default=-1)

    class Meta:
        unique_together = ('user', 'client_id',)


class Payment(models.Model):
    status = models.TextField(default='')
    terminal_key = models.TextField(default='')
    payment_id = models.TextField(default='')
    order_id = models.TextField(default='', unique=True)
    amount = models.BigIntegerField(default=0)
    payment_url = models.TextField(default='')

    # 0 | 1
    is_wallet = models.IntegerField(default=0)

    is_processed = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    is_refunded = models.BooleanField(default=False)

    date = models.DateTimeField(default=None, null=True, blank=True)

    user = models.ForeignKey(
        Account, blank=False, null=False, related_name='payment_actor', on_delete=models.CASCADE)
