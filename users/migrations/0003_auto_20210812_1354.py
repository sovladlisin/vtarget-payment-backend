# Generated by Django 3.0.3 on 2021-08-12 06:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210811_1746'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vkprofile',
            old_name='img',
            new_name='photo',
        ),
    ]
