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
