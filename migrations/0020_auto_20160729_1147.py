# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-29 16:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoreo', '0019_sensor_seconds_data_send'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sensor',
            old_name='nombre',
            new_name='alias',
        ),
    ]
