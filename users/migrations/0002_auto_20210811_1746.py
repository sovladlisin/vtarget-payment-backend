# Generated by Django 3.0.3 on 2021-08-11 10:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vkprofile',
            old_name='vk_img',
            new_name='img',
        ),
        migrations.RenameField(
            model_name='vkprofile',
            old_name='vk_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='vkprofile',
            old_name='vk_token',
            new_name='token',
        ),
    ]
