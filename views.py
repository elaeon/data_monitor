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
    return render (request, 'alerta/monitor.html', {'sensores':Sensor.objects.filter(estado=True) })
