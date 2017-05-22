# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
import requests
from django.core.mail import EmailMessage, send_mail
from django.core.urlresolvers import reverse
from django.conf import settings
from datetime import date, datetime,time
import urllib, urllib2, json
import os
import datetime
import io


class Sensor(models.Model):
    url_sensor = models.URLField(blank=False, null=False)
    nombre = models.CharField(blank=False, null=True, max_length=50)
    alias = models.CharField(blank=False, max_length=50)
    estado = models.BooleanField(default= True)
    url_dashboard = models.URLField(blank=True, null=True)
    group_name = models.CharField(blank=True, null=True, max_length=50)
    type = models.CharField(choices=(("c", "continuos"), ("d", "discrete")), max_length=2)

    def valor_actual(self):
        try:
            return self.datos(60)[-1]
        except IndexError:
            return None

    def valor_actual_round(self):
        if self.valor_actual():
            return round(self.valor_actual()[0], 2)
        
    def __unicode__(self):
        return u"%s" % self.alias
        
    def datos(self, seconds):
        URL_PARAMS = "render?target={name}&format=json".format(name=self.nombre)
        url = os.path.join(self.url_sensor, URL_PARAMS + "&from=-{}s".format(seconds))
        datos = requests.get(url).json()
        datos = datos[0]['datapoints']
        return filter(lambda x: x[0] is not None, datos)

    def datos_date(self, from_, until):
        URL_PARAMS = "render?target={name}&format=json".format(name=self.nombre)
        url = os.path.join(self.url_sensor, URL_PARAMS + "&from={}&until={}".format(from_, until))
        datos = requests.get(url).json()
        datos = datos[0]['datapoints']
        return filter(lambda x: x[0] is not None, datos)

    def sensor_graph(self, seconds):
        import base64
        URL_PARAMS = "render?target={name}&format=png".format(name=self.nombre)
        url = os.path.join(self.url_sensor, URL_PARAMS + "&from=-{}s".format(seconds))
        buf = io.BytesIO()
        request = requests.get(url, stream=True)
        if request.status_code == 200:
            for chunk in request.iter_content(1024):
                buf.write(chunk)
        buf.seek(0)
        return base64.b64encode(buf.read())

    def sensor_graph_url(self, seconds):
        URL_PARAMS = "render?target={name}&format=png".format(name=self.nombre)
        url = os.path.join(self.url_sensor, URL_PARAMS + "&from=-{}s".format(seconds))
        return url

@python_2_unicode_compatible        
class Persona(models.Model):
    nombre = models.CharField(blank= False, null=True,max_length=100)
    email =models.EmailField(blank= False, null=True)
    numero_celular = models.CharField(blank= True, null=True,max_length= 10)
    id_telegram = models.CharField(blank= True, null=True,max_length= 10)

    def __str__(self):
        return u"%s" % self.nombre

        
class Alerta(models.Model):
    prob_critica = models.FloatField("Porcentaje", default=0)
    seconds_to_check = models.IntegerField(blank=True, null=True)
    sensor = models.ForeignKey(Sensor, blank=True, null=True)
    valor_de_alerta = models.FloatField()
    tipo_valor_de_alerta = models.CharField(max_length=10,
        choices=(("maximo", "maximo"), ("minimo", "minimo")), db_index=True)
    persona = models.ManyToManyField(Persona)
    nivel_de_alerta = models.CharField("Nivel de alerta", max_length=10,
        choices=(("tolerable", "tolerable"), ("critico", "critico")), db_index=True)

    telegram = models.BooleanField(default=False)
    correo = models.BooleanField(default=False)
    sms = models.BooleanField(default=False)

    def minutes_to_check(self):
        return self.seconds_to_check / 60

    def __unicode__(self):
        return u"%s sensor " % (self.sensor,)

    def personas_por_alertar(self):
        return ", ".join([u"%s" % x for x in self.persona.all()])

    def in_anormal_levels(self):
        datos  = self.sensor.datos(self.seconds_to_check)
        datos = [temp for temp, _ in datos]
        avg = sum(datos) / float(len(datos))
        return self.temp_values_above_p(
            datos, self.valor_de_alerta, self.tipo_valor_de_alerta, self.prob_critica), avg

    def tpl_activo_msg_SMS(self):
        return u"""{} en "{}".Se activo alarma en {}C. Silenciar alarma {}"""
        
    def tpl_activo_msg(self):
        return u"""Se ha detectado un {} de temperatura en "{}". La temperatura promedio en la que se activo la alarma fue de {}°C. Para silenciar la alarma ingrese a {}"""

    def tpl_inactivo_msg(self):
        return u"""Se ha desactivado la alarma en "{}"."""

    def enviar_correo_desactivada(self):
        cadena_des = self.tpl_inactivo_msg()
        cadena_des = cadena_des.format(self.sensor.alias)
        for persona in self.persona.all():
            print u"Persona a enviar: %s" % persona.email
            msg = EmailMessage(
                "Alerta desactivada", cadena_des, settings.DEFAULT_FROM_EMAIL, [persona.email]) 
            msg.send()

    def enviar_correo(self):
        url_des = u'{}{}'.format(settings.URL_BASE, 
            reverse('silenciar_alerta', args=[self.sensoralertado.id]))
        cadena_des = self.tpl_activo_msg()
        temp_redondeado = round(self.sensoralertado.temp, 2)
        if self.tipo_valor_de_alerta == "maximo":
            cadena_des = cadena_des.format(
                "incremento", self.sensor.alias, temp_redondeado, url_des)
        elif self.tipo_valor_de_alerta == "minimo":
            cadena_des =  cadena_des.format(
                "decremento", self.sensor.alias, temp_redondeado, url_des)

        for persona in self.persona.all():
            print u"Persona a enviar: %s" % persona.email        
            #msg = EmailMessage("Alerta", cadena_des, settings.DEFAULT_FROM_EMAIL, [persona.email]) 
            #msg.send()
            send_mail('Alerta', cadena_des, settings.DEFAULT_FROM_EMAIL, 
                [persona.email], fail_silently=False)
            print("se envio correo")
        
    def enviar_telegram(self):#new_alert objeto SensorAlertado
        url_des = u'{}{}'.format(settings.URL_BASE, reverse('silenciar_alerta', args=[self.sensoralertado.id]))
        cadena_des = self.tpl_activo_msg()
        temp_redondeado = round(self.sensoralertado.temp, 2)        
        if self.tipo_valor_de_alerta == "maximo":
            cadena_des = cadena_des.format(
                "incremento", self.sensor.alias, temp_redondeado, url_des)
        elif self.tipo_valor_de_alerta == "minimo":
            cadena_des = cadena_des.format(
                "decremento", self.sensor.alias, temp_redondeado, url_des)

        url = "https://api.telegram.org/bot{}/sendMessage".format(settings.BOT_ID)
        for persona in self.persona.all():
            print u"Persona a enviar: %s" % persona.email
            try:
                result = urllib2.urlopen(url, 
                    urllib.urlencode({ "chat_id": persona.id_telegram, 
                                    "text": cadena_des.encode("utf8") })).read()
            except urllib2.HTTPError:
                print "NO SE ENVIO TELEGRAM, NO SE TIENE numero de telegram"
            else:
                print u"se envio telegram"
        #print cadena_des

    def enviar_telegram_desactivada(self):
        cadena_des = self.tpl_inactivo_msg()
        cadena_des = cadena_des.format(self.sensor.alias)        
        url = "https://api.telegram.org/bot{}/sendMessage".format(settings.BOT_ID)
        for persona in self.persona.all():
            try:
                result = urllib2.urlopen(url, 
                    urllib.urlencode({ "chat_id": persona.id_telegram, 
                                        "text": cadena_des.encode('utf8') })).read()
            except urllib2.HTTPError:
                print "NO SE ENVIO TELEGRAM, NO SE TIENE numero de telegram"
            else:
                print u"se envio telegram"

    def enviar_sms(self):
        url_des = u'{}{}'.format(
            settings.URL_BASE, reverse('silenciar_alerta', args=[self.sensoralertado.id]))
        cadena_des = self.tpl_activo_msg_SMS()
        temp_redondeado = round(self.sensoralertado.temp, 2)
        if self.tipo_valor_de_alerta == "maximo":
            cadena_des = cadena_des.format(
                "incremento", self.sensor.alias, temp_redondeado, url_des)
        elif self.tipo_valor_de_alerta == "minimo":
            cadena_des = cadena_des.format(
                "decremento", self.sensor.alias, temp_redondeado, url_des)

        for persona in self.persona.all():

            #print cadena_des.encode("utf8")

            parametros = urllib.urlencode({
                u'apikey': settings.LLAVE_API, 
                u'mensaje': cadena_des.encode("utf8"),
                u'numcelular': persona.numero_celular, 
                u'numregion': u'52'})
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept":"text/plain"}
            request = urllib2.Request(
                'http://www.smsmasivos.com.mx/sms/api.envio.new.php', parametros, headers)
            opener = urllib2.build_opener()
            respuesta = opener.open(request).read()
            #print(json.loads(respuesta))

    def enviar_sms_desactivada(self):
        cadena_des = self.tpl_inactivo_msg()        
        cadena_des = cadena_des.format(self.sensor.alias)
        for persona in self.persona.all():
            parametros = urllib.urlencode({
                'apikey': settings.LLAVE_API,
                'mensaje': cadena_des,
                'numcelular': persona.numero_celular,
                'numregion':'52'})
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept":"text/plain"}
            request = urllib2.Request(
                'http://www.smsmasivos.com.mx/sms/api.envio.new.php', parametros, headers)
            opener = urllib2.build_opener()
            respuesta = opener.open(request).read()
            #print(json.loads(respuesta))
    
    def envio_mensaje_apagado_alarma(self):
        if self.telegram:
            self.enviar_telegram_desactivada()
        if self.correo:
            self.enviar_correo_desactivada()
        if self.sms:
            self.enviar_sms_desactivada()

    def color_actual(self):
        valor_actual=self.sensor.valor_actual() 
        #if valor_actual is None: 
        return 'circleStatsItemBox black' 
        '''
        elif ( valor_actual<self.nivel_min) :
            return  'circleStatsItemBox red'
        elif ( valor_actual < self.nivel_min + self.minus_nivel_min ) :
            return  'circleStatsItemBox yellow'
        elif ( valor_actual<self.nivel_max-self.minus_nivel_max) :
            return 'circleStatsItemBox green'
        elif ( valor_actual<self.nivel_max ) : 
            return 'circleStatsItemBox yellow' 
        else:
            return 'circleStatsItemBox red'
        '''
    @classmethod
    def temp_values_above_p(self, values, limit_value, type_limit_value, p):
        total_length = float(len(values))
        if type_limit_value == "maximo":
            out_range = filter(lambda x: x > limit_value, values)
        else:
            out_range = filter(lambda x: x < limit_value, values)
        #print("####### P:", len(out_range) / total_length)
        return (len(out_range) / total_length) > p

    def valor_calc(self):
        datos  = self.sensor.datos(self.seconds_to_check)
        datos = [temp for temp, _ in datos]
        out_r, in_r = self.valor_prob(
                datos, self.valor_de_alerta, self.tipo_valor_de_alerta, self.prob_critica)
        if self.alertado():
            return out_r
        else:
            return in_r

    @classmethod
    def valor_prob(self, values, limit_value, type_limit_value, p):
        if type_limit_value == "maximo":
            out_range = filter(lambda x: x > limit_value, values)
            in_range = filter(lambda x: x < limit_value, values)
        else:
            out_range = filter(lambda x: x < limit_value, values)
            in_range = filter(lambda x: x > limit_value, values)

        try:
            out_r = round(sum(out_range) / len(out_range), 1)
        except ZeroDivisionError:
            out_r = None

        try:
            in_r = round(sum(in_range) / len(in_range), 1)
        except ZeroDivisionError:
            in_r = None

        return (out_r, in_r)

    def activate(self, temp_avg):
        ahora = datetime.datetime.now()
        try:
            self.sensoralertado.temp = temp_avg
            self.sensoralertado.fecha = ahora
            self.sensoralertado.activado = True
            self.sensoralertado.save()
        except SensorAlertado.DoesNotExist:
            SensorAlertado.objects.create(
                alerta=self,
                fecha=ahora,
                temp=temp_avg,
                activado=True)

    def desactivate(self):
        try:
            if self.sensoralertado.activado:
                self.sensoralertado.activado = False
                self.sensoralertado.save()
                self.envio_mensaje_apagado_alarma()
        except SensorAlertado.DoesNotExist:
            pass

    def send_msg_alert(self):
        if self.telegram:
            #print("TELEGRAM")
            self.enviar_telegram()
        if self.correo:
            #print("CORREO")
            self.enviar_correo()

        if self.sms:
            self.enviar_sms()

        self.sensoralertado.alert_msg_date = datetime.datetime.now()
        self.sensoralertado.save()


    def send_msg_alert_check_mute(self):
        ahora = datetime.datetime.now()
        try:
            alert = self.sensoralertado.activado
            if self.sensoralertado.mute_date is not None:
                if (ahora - self.sensoralertado.mute_date).seconds >= settings.TIEMPO_MUTE: # 86400   1 day = 60*60*24
                    self.sensoralertado.mute_date = None
                    self.sensoralertado.alert_msg_date = None
                    self.sensoralertado.save()
                    alert = alert and True
                else:
                    alert = False

            if alert:
                if self.sensoralertado.alert_msg_date is None:
                    self.send_msg_alert()
                elif (ahora - self.sensoralertado.alert_msg_date).seconds >= settings.TIEMPO_ENVIO_ALERTAS: #10 minutes
                    self.send_msg_alert()
                    
        except SensorAlertado.DoesNotExist:
            pass

    def alertado(self):
        return SensorAlertado.objects.filter(alerta=self, activado=True)


class SensorAlertado(models.Model):
    alerta = models.OneToOneField(Alerta)
    fecha = models.DateTimeField()
    temp = models.FloatField() #temperatura promedio
    user = models.ForeignKey(User, blank=False, null=True)
    activado = models.BooleanField(default=True)
    mute_date = models.DateTimeField(blank=True, null=True)    
    alert_msg_date = models.DateTimeField(blank=True, null=True)


    def mute_date_hasta(self):
        from datetime import datetime, timedelta
        fecha_limite_mute = None

        if self.mute_date:
            delta_de_tiempo = timedelta(seconds=settings.TIEMPO_MUTE)
            fecha_limite_mute = self.mute_date + delta_de_tiempo

        return fecha_limite_mute

