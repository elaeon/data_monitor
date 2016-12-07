# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import MultipleObjectsReturned
from monitoreo.models import Sensor, Persona, Alerta, SensorAlertado
from datetime import datetime, time
import urllib,urllib2,json
import numpy as np

class Command(BaseCommand):
    help = 'verifica minimo y maximo'
    
    def handle(self, *args, **options):
        try:
            sensor = Sensor.objects.get(id=6)
            print "************************************************************************"
            print "%s alias: %s  estado: %s" % (sensor.nombre, sensor.alias, sensor.estado)
            #data = np.asarray(sensor.datos_date("08:00_20161201", "18:00_20161205"))
            data_temp = np.asarray(sensor.datos(604800))
            print(round(data_temp.mean(axis=0)[0], 2))
            print(round(data_temp.std(axis=0)[0], 2))

            sensor = Sensor.objects.get(id=7)
            data2 = np.asarray(sensor.datos(604800))#_date("08:00_20161201", "18:00_20161206"))
            count_value_change(data2, data_temp)
            #sensor.sensor_graph(3600)
        except Sensor.DoesNotExist:
            raise CommandError('Sensor does not exist')


class Cicle(object):
    def __init__(self):
        self.t0 = None
        self.t1 = None

    def set_t0(self, t):
        self.t0 = datetime.utcfromtimestamp(t)

    def set_t1(self, t):
        self.t1 = datetime.utcfromtimestamp(t)

    def diff(self):
        if self.t0 is not None and self.t1 is not None:
            return (self.t1 - self.t0).total_seconds()
        else:
            print("t0", self.t0)
            print("t1", self.t1)
            print("ERROR")


class State(object):
    def __init__(self, initial=0):
        self.v0 = initial
        self.elems = []
        self.open = False

    def cmp(self, v, t):
        if v != self.v0 and not self.open:
            cicle = Cicle()
            cicle.set_t0(t)
            self.elems.append(cicle)
            self.open = True
        elif v == self.v0 and self.open:
            cicle = self.elems.pop()
            cicle.set_t1(t)
            self.elems.append(cicle)
            self.open = False

    def calc_avg_open(self):
        return sum(elem.diff() for elem in self.elems) / len(self.elems)

    def min(self):
        return min(elem.diff() for elem in self.elems)

    def max(self):
        return max(elem.diff() for elem in self.elems)

    def distance_avg(self, elems, ignore=3600):
        ts = 0
        counter = 0
        for open0, open1 in zip(elems, elems[1:]):
            interval = (open1.t0 - open0.t1).total_seconds()
            if interval <= ignore:
                ts += interval
                counter += 1
        counter = 1 if counter == 0 else counter
        return round(ts / float(counter)), round(float(counter) / (len(elems) - 1), 2), counter

    def cut_working_hours(self, init, end):
        groups = {}
        i = self.elems[0].t0.day
        for elem in self.elems:
            if (elem.t0.time() >= init.time() or elem.t1.time() >= init.time()) and\
                (elem.t0.time() <= end.time() or elem.t1.time() <= end.time()):
                key = elem.t0.day - i
                groups.setdefault(key, [])
                groups[key].append(elem)
            else:
                print(elem.t0)
        return groups


mod = {0:60, 1:60, 2:24, 3:365}
def _seconds2human(v, deep=0):
    d, r = divmod(v, mod[deep])
    if d == 0:
        return [r]
    else:
        o = _seconds2human(d, deep=deep+1)
        o.append(r)
        return o


def seconds2human(v):
    values = map(str, _seconds2human(int(v)))
    scales = ["d", "h", "m", "s"]
    scales = scales[-len(values):]
    return " ".join(v+s for v, s in zip(values, scales))


def cut_serie_g(serie, groups):
    serie_groups = {}
    index = 0
    counter = 0
    for key, items in groups.items():
        for v, t in serie[index:]:
            t = datetime.utcfromtimestamp(t)
            counter += 1
            if items[0].t0.time() <= t.time() <= items[-1].t1.time() and t.date() == items[0].t0.date():
                serie_groups.setdefault(key, [])
                serie_groups[key].append(v)
            elif t.time() > items[-1].t1.time() and t.date() == items[0].t0.date():
                index = counter
                break
    return serie_groups


def count_value_change(data, data_temp, initial=0):
    state = State(initial=initial)
    init_d = datetime.fromtimestamp(data[0][1])
    end_d = datetime.fromtimestamp(data[-1][1])
    days = (end_d - init_d).days
    for elem, t in data:
        state.cmp(elem, t)
    print("AVG", seconds2human(state.calc_avg_open()))
    print("MIN", seconds2human(state.min()))
    print("MAX", seconds2human(state.max()))
    print("APERTURAS", len(state.elems), len(state.elems)/days)
    g = state.cut_working_hours(datetime(2016, 12, 1, 14, 0), datetime(2016, 12, 2, 23, 59))
    gt = cut_serie_g(data_temp, g)
    for k, ci in g.items():
        v, c, t = state.distance_avg(ci)
        print("APERTURAS CONSECUTIVAS AVG", seconds2human(v), c, t, round(np.asarray(gt[k]).mean(), 1), ci[0].t0.strftime("%Y-%m-%d"))
    print("T", seconds2human((end_d - init_d).total_seconds()))
