# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-04 17:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoreo', '0028_auto_20160804_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alerta',
            name='prob_critica',
            field=models.FloatField(default=0, verbose_name='Probalilidad'),
        ),
        migrations.AlterField(
            model_name='sensoralertado',
            name='fecha',
            field=models.DateTimeField(),
        ),
    ]