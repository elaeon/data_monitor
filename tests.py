# -*- coding: utf-8 -*-
from django.test import TestCase
from monitoreo.models import Sensor, Alerta, Persona


#####
#   TODAS LAS PRUEBAS SE REALIZAN EN EL INTERVALO DE [-20, -10]
#####

MAXIMO = -10
MINIMO = -20

class AlertaTestCase(TestCase):
    def setUp(self):
        sensor = Sensor.objects.create(
            url_sensor="http://carbon.inmegen.gob.mx/",
            nombre="sensors.limon161.temperature_low_one",
            alias="congelador_limon161",
            estado = True)
        persona = Persona.objects.create(
            nombre=u"Ramiro Vázquez",
            email="rvazquez@inmegen.gob.mx",
            numero_celular="",
            id_telegram="233307082")
        self.alerta = Alerta.objects.create(
            prob_critica=.9,
            sensor=sensor,
            valor_de_alerta=MAXIMO,
            tipo_valor_de_alerta="maximo",
            nivel_de_alerta="tolerable",
            correo=True,
            telegram=True)
        self.alerta.persona.add(persona)

    def test_random_data_in(self):
        """Checamos si se manda alertas con valores aleatorios dentro del intervalo
            [-20, -10]
        """
        data = list(create_sample_random(12, MINIMO, MAXIMO))
        self.assertEqual(Alerta.temp_values_above_p(data, MAXIMO, 'maximo', 0), False)
        self.assertEqual(Alerta.temp_values_above_p(data, MINIMO, 'minimo', 0), False)

    def test_data_20(self):
        """Generamos valores en el intervalo -20 a -10 con un 21% de probabilidad de que
        salgan del intervalo"""
        data = create_sample_bernoulli(20000, MAXIMO, 'maximo', .21)
        self.assertEqual(Alerta.temp_values_above_p(list(data), MAXIMO, 'maximo', .2), True)
        data = create_sample_bernoulli(20000, MINIMO, 'minimo', .21)
        self.assertEqual(Alerta.temp_values_above_p(list(data), MINIMO, 'minimo', .2), True)

    def test_data_80(self):
        """Generamos valores en el intervalo -20 a -10 con un 81% de probabilidad de que
        salgan del intervalo"""
        data = create_sample_bernoulli(20000, MAXIMO, 'maximo', .81)
        self.assertEqual(Alerta.temp_values_above_p(list(data), MAXIMO, 'maximo', .8), True)
        data = create_sample_bernoulli(20000, MINIMO, 'minimo', .81)
        self.assertEqual(Alerta.temp_values_above_p(list(data), MINIMO, 'minimo', .8), True)

    def test_data_no_alert(self):
        """Generamos valores en el intervalo -20 a -10 con un 21% y 75% de probabilidad de que
        salgan del intervalo, mientras que la tolerancia es de 80%"""
        data = create_sample_bernoulli(20000, MAXIMO, 'maximo', .21)
        self.assertEqual(Alerta.temp_values_above_p(list(data), MAXIMO, 'maximo', .8), False)
        data = create_sample_bernoulli(20000, MINIMO, 'minimo', .75)
        self.assertEqual(Alerta.temp_values_above_p(list(data), MINIMO, 'minimo', .8), False)

    def test_send_alert(self):
        self.alerta.send(MAXIMO + 1)


def create_sample_random(length, minimo, maximo):
    import random
    for i in range(length):
        yield random.uniform(minimo, maximo)


def create_sample_bernoulli(length, limit_value, type_limit_value, p):
    import random
    if type_limit_value == 'minimo':
        low = limit_value
        up = limit_value + 5
        low_plus = limit_value - 5
        up_plus = limit_value - 1
    else:
        low = limit_value - 5
        up = limit_value
        low_plus = limit_value + 1
        up_plus = limit_value + 5

    for i in range(length):
        #IN DATA
        if p <= random.uniform(0, 1):
            yield random.uniform(low, up)
        #OUT DATA
        else:
            yield random.uniform(low_plus, up_plus)
