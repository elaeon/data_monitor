# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest
from .models import Sensor, Alerta, Persona, SensorAlertado
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required(login_url=settings.RUTA_LOGIN)
def silenciar_alerta(request, sensor_alertado_id):
    from datetime import datetime, timedelta

    sensor_alertado = get_object_or_404(SensorAlertado, pk=sensor_alertado_id)
    ahora = datetime.now()

    sensor_alertado.user = request.user
    sensor_alertado.mute_date = ahora
    sensor_alertado.save()

    delta_de_tiempo = timedelta(seconds=settings.TIEMPO_MUTE)

    fecha_limite_mute = ahora + delta_de_tiempo #86400: #1 day = 60*60*24

    messages.success(request, u'La alarma esta en mute hasta el %s' % fecha_limite_mute)     

    return render(request, 'alerta/crear.html', {})


@login_required(login_url=settings.RUTA_LOGIN)    
def monitor_actual (request):
    return render (request, 'alerta/monitor.html', {'sensores': Sensor.objects.filter(estado=True) })


@login_required(login_url=settings.RUTA_LOGIN)
def sensor_groups_details(request, group_name):
    from monitoreo.utils import monitor_details

    one_week = 604800
    sensor_c = Sensor.objects.get(estado=True, group_name=group_name, type='c')
    sensor_d = Sensor.objects.get(estado=True, group_name=group_name, type='d')
    sensores_detail = monitor_details(sensor_c, sensor_d, one_week)
    sensor_c_img = sensor_c.sensor_graph(one_week)
    sensor_d_img = sensor_d.sensor_graph(one_week)
    return render (request, 'alerta/monitor_details.html', {
        'sensores_detail': sensores_detail, 
        'sensor_c_img': sensor_c_img,
        'sensor_d_img': sensor_d_img
        })
