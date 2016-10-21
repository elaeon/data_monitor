# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import MultipleObjectsReturned
from monitoreo.models import Sensor, Persona, Alerta, SensorAlertado
from datetime import datetime, time
import urllib,urllib2,json


class Command(BaseCommand):
    help = 'verifica minimo y maximo'
    
    def handle(self, *args, **options):
        try:
            sensores = Sensor.objects.filter(estado=True)
            for sensor in sensores:
                print "************************************************************************"
                print "%s alias: %s  estado: %s" % (sensor.nombre, sensor.alias, sensor.estado)

                for alerta in sensor.alerta_set.all():
                    in_anormal_levels, temp_avg = alerta.in_anormal_levels()
                    print("Sensor", sensor.nombre, sensor.alias)
                    print "Valor de alerta: %s" % alerta.valor_de_alerta
                    print "Alerta: %s, %s" % (in_anormal_levels, temp_avg)
                    print "##---"
                    if in_anormal_levels:
                        alerta.activate(temp_avg)
                    else:
                        alerta.desactivate()
        except Sensor.DoesNotExist:
            raise CommandError('Sensor does not exist')
