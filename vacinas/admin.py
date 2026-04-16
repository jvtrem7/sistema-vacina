from django.contrib import admin
from .models import Paciente, Vacina 

admin.site.register(Paciente)
admin.site.register(Vacina)