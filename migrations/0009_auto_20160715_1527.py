# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-15 20:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoreo', '0008_auto_20160715_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intervalo',
            name='nivel_max',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='intervalo',
            name='nivel_min',
            field=models.FloatField(default=0, null=True),
        ),
    ]
