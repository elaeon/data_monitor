# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-06 23:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alerta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('estado', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Intervalo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nivel_max', models.IntegerField(default=0, null=True)),
                ('nivel_min', models.IntegerField(default=0, null=True)),
                ('corrimiento', models.IntegerField(default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('numero_celular', models.CharField(blank=True, max_length=10, null=True)),
                ('id_telegram', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_sensor', models.URLField()),
                ('nombre', models.CharField(max_length=50)),
                ('estado', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='intervalo',
            name='persona',
            field=models.ManyToManyField(to='monitoreo.Persona'),
        ),
        migrations.AddField(
            model_name='intervalo',
            name='sensor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitoreo.Sensor'),
        ),
        migrations.AddField(
            model_name='alerta',
            name='intervalo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitoreo.Intervalo'),
        ),
    ]
