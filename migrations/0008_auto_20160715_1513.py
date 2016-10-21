# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-15 20:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoreo', '0007_auto_20160715_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intervalo',
            name='corrimiento',
            field=models.IntegerField(default=0, help_text='numero de datos seguidos a los que se activa la alarma, en 1 minuto son maximo 12 elementos', null=True),
        ),
    ]
