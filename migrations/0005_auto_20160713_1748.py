# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-13 22:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoreo', '0004_auto_20160711_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='intervalo',
            name='minus_nivel_max',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='intervalo',
            name='minus_nivel_min',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
