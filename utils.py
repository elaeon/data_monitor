# -*- coding: utf-8 -*-
from datetime import datetime, time
import numpy as np


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
        elif self.t1 is not None:
            self.set_t1(datetime.datetime.utcnow())
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
    render = {}
    state = State(initial=initial)
    init_d = datetime.fromtimestamp(data[0][1])
    end_d = datetime.fromtimestamp(data[-1][1])
    days = (end_d - init_d).days
    for elem, t in data:
        state.cmp(elem, t)
    render["d_avg"] = seconds2human(state.calc_avg_open())
    render["d_min"] = seconds2human(state.min())
    render["d_max"] = seconds2human(state.max())
    render["n_elems"] = (len(state.elems), len(state.elems) / days)
    g = state.cut_working_hours(datetime(2016, 12, 1, 14, 0), datetime(2016, 12, 2, 23, 59))
    gt = cut_serie_g(data_temp, g)
    render["consecutivos"] = []
    for k, ci in g.items():
        interval_avg, open_avg, open_total = state.distance_avg(ci)
        open_total_avg = seconds2human(sum(elem.diff() for elem in ci) / len(ci))
        render["consecutivos"].append((seconds2human(interval_avg), open_avg, open_total, open_total_avg, round(np.asarray(gt[k]).mean(), 1), ci[0].t0.strftime("%Y-%m-%d")))
    render["total_time"] = seconds2human((end_d - init_d).total_seconds())
    return render


def monitor_details(sensor_c, sensor_d, period):
    render = {}
    render["nombre"] = sensor_c.nombre
    #data = np.asarray(sensor.datos_date("08:00_20161201", "18:00_20161205"))
    data_temp = np.asarray(sensor_c.datos(period))
    render["avg"] = round(data_temp.mean(axis=0)[0], 2)
    render["std"] = round(data_temp.std(axis=0)[0], 2)
    data2 = np.asarray(sensor_d.datos(period))#_date("08:00_20161201", "18:00_20161206"))
    render.update(count_value_change(data2, data_temp))
    return render

def resume(values):
    if len(values) > 0:
        ti = values[0][1] 
        tf = values[-1][1]
        ti = datetime.utcfromtimestamp(ti)
        tf = datetime.utcfromtimestamp(tf)
        seconds = (tf - ti).seconds
        return abs(values[0][0] - values[-1][0]), seconds
    return 0, 0
  

def radio(dec, inc):
    v, t = dec
    dec_unit = t / float(v)
    v, t = inc
    inc_unit = t / float(v)
    return dec_unit / inc_unit


def calc_decrement_inc(data):
    l_increment = []
    l_decrement = []
    resume_i = []
    resume_d = []
    i = False
    d = False
    for (v0, t0), (v1, t1) in zip(data, data[1:]):
        #print(v0, v1)
        if v0 > v1:
            #print("D", v1, v0)
            if len(l_increment) > 0:
                resume_i.append(resume(l_increment))
                l_increment = []
            l_decrement.append((v0, t0))
            l_decrement.append((v1, t1))
            i = False
            d = True
        elif v1 > v0:
            #print("I", v1, v0)
            if len(l_decrement) > 0:
                resume_d.append(resume(l_decrement))
                l_decrement = []
            l_increment.append((v0, t0))
            l_increment.append((v1, t1))
            i = True
            d = False
        else:
            if d:
                l_decrement.append((v0, t0))
                l_decrement.append((v1, t1))
            elif i:
                l_increment.append((v0, t0))
                l_increment.append((v1, t1))
    if len(l_decrement) > 0:
        resume_d.append(resume(l_decrement))
    if len(l_increment) > 0:
        resume_i.append(resume(l_increment))

    #print(resume_d)
    import heapq
    decrement = np.asarray(heapq.nlargest(3, resume_d, key=lambda x:x[0])).mean(axis=0)
    increment = np.asarray(heapq.nlargest(3, resume_i, key=lambda x:x[0])).mean(axis=0)
    print(max(resume_d, key=lambda x:x[0]), max(resume_i, key=lambda x:x[0]))
    return decrement, increment

def test():
    import requests
    url = "http://carbon.inmegen.gob.mx/render/?target=sensors.limon161.temperature_low_one&format=json&from=09:25_20161201&until=19:50_20161220"
    r = requests.get(url)
    data = r.json()[0]
    data = filter(lambda x: x[0] is not None, data['datapoints'])
    d, i = calc_decrement_inc(data)
    print(d, i)
    print(radio(d, i))
