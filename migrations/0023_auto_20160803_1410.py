# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-03 19:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoreo', '0022_auto_20160803_1351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sensor',
            name='seconds_data_send',
        ),
        migrations.AddField(
            model_name='alerta',
            name='seconds_data_send',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
