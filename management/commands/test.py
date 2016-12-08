# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from monitoreo.models import Sensor
from monitoreo.utils import monitor_details

class Command(BaseCommand):
    help = 'verifica minimo y maximo'
    
    def handle(self, *args, **options):
        try:
            group_name = "coco"
            sensor_c = Sensor.objects.get(estado=True, group_name=group_name, type='c')
            sensor_d = Sensor.objects.get(estado=True, group_name=group_name, type='d')
            sensores_detail = monitor_details(sensor_c, sensor_d)
            print "************************************************************************"
            print "%s alias: %s  estado: %s" % (sensor_c.nombre, sensor_c.alias, sensor_c.estado)
            #data = np.asarray(sensor.datos_date("08:00_20161201", "18:00_20161205"))
            print(sensores_detail)
        except Sensor.DoesNotExist:
            raise CommandError('Sensor does not exist')



