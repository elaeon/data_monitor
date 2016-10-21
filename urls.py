from django.conf.urls import url

from . import views

urlpatterns = [
#    url(r'^$', views.index, name='index'),
    url(r'^(?P<sensor_alertado_id>[0-9]+)/silenciar/$', views.silenciar_alerta, name='silenciar_alerta'), 
    url(r'^monitor/$' , views.monitor_actual, name= 'monitor_actual'),   
#    url(r'^(?P<reporte_id>[0-9]+)/caso/(?P<caso_id>[0-9]+)/paso-2/$', views.caso_reporte_paso_2, name='caso_reporte_paso_2'),    
]
