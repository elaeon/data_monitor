# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-11 22:14
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoreo', '0002_alerta_temp'),
    ]

    operations = [
        migrations.AddField(
            model_name='alerta',
            name='fecha_fin',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 11, 17, 14, 44, 837321)),
        ),
        migrations.AddField(
            model_name='alerta',
            name='fecha_inicio',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 11, 17, 14, 44, 837228)),
        ),
    ]