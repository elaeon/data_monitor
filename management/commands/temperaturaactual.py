# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from monitoreo.models import Sensor, Intervalo, Persona, Alerta
from django.conf import settings
import urllib, urllib2, json


class Command(BaseCommand):
    help = 'verifica minimo y maximo'

    def handle(self, *args, **options):
        persona= Persona.objects.get(id_telegram="203383748")
        intervalo = Intervalo.objects.all()
        for i in intervalo:
            personas=i.persona.all()
        for p in personas:
            if p == persona:
                bot_id = "182997279:AAH2ddeTGJs3KEye4W1dkYaKKn60950qQqg"
                try:
                    sensor=i.sensor
                    url= 'http://carbon.inmegen.gob.mx/render?target=sensors.%s&format=json&from=-1s' %sensor.nombre
                    auxiliar = urllib.urlopen(url).read()
                    valores = json.loads(auxiliar)
                    valor=valores[0]['datapoints']
                    v=valor[0][0]
                    result = urllib2.urlopen("https://api.telegram.org/bot" + bot_id + "/sendMessage", urllib.urlencode({ "chat_id": persona.id_telegram, "text": 'La temperatura actual del sensor es: %s   grados' % v })).read()
                except Sensor.DoesNotExist:
            raise CommandError('Sensor "%s" does not exist' % i.sensor)
