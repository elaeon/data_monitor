# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-15 20:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('monitoreo', '0009_auto_20160715_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alerta',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
