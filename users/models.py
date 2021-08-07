from django.db import models
import datetime
# Create your models here.


class VkUser(models.Model):
    user_id = models.BigIntegerField(default=0)
    user_img = models.CharField(default='Не указано', max_length=300)
    user_name = models.CharField(default='Не указано', max_length=300)
    token = models.CharField(default='', max_length=300)

    is_admin = models.BooleanField(default=False)
