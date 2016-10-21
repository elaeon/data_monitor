from django.contrib import admin
from monitoreo.models import *

# Register your models here.
class SensorAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_filter = ['estado',]
    list_display = ['id', 'url_sensor', 'nombre', 'alias', 'estado']


class PersonaAdmin(admin.ModelAdmin):
    list_per_page = 25
    #list_filter = ['estado',]
    list_display = ['nombre', 'email', 'id_telegram']

class AlertaAdmin(admin.ModelAdmin):
    list_per_page = 25
    #list_filter = ['estado',]
    list_display = ['sensor', 'valor_de_alerta', 'tipo_valor_de_alerta', 'nivel_de_alerta',
    'telegram', 'correo', 'sms']

class SensorAlertadoAdmin(admin.ModelAdmin):
    list_per_page = 25
    #list_filter = ['sensor',]
    list_display = ['id', 'alerta', 'fecha', 'activado']


admin.site.register(SensorAlertado, SensorAlertadoAdmin)
admin.site.register(Sensor, SensorAdmin)
#admin.site.register(Intervalo)
admin.site.register(Persona, PersonaAdmin)
admin.site.register(Alerta, AlertaAdmin)

