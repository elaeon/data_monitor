# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from monitoreo.models import Alerta
import datetime

class Command(BaseCommand):
    help = 'enviar alarmas'
    
    def handle(self, *args, **options):
        alertas = Alerta.objects.filter(sensoralertado__activado=True)
        for alerta in alertas:
            alerta.send_msg_alert_check_mute()

        if alertas.count() == 0:
            print(u"no hay envio, no hay alertas activas.")

              
              
                   
                
                

                        
        
