from django.contrib import admin
from .models import Paciente, Vacina, Estoque, PostoSaude

admin.site.register(Paciente)
admin.site.register(Vacina)
admin.site.register(PostoSaude)
admin.site.register(Estoque)