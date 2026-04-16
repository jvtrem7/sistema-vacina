from django.contrib import admin
from django.urls import path
from vacinas.views import home 
from vacinas import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), 
    path('novo-paciente/', views.cadastrar_paciente, name='cadastrar_paciente'),
    path('registrar-dose/', views.registrar_dose, name='registrar_dose'),
    path('pacientes/', views.listar_pacientes, name='listar_pacientes'),
    path('editar-paciente/<int:pk>/', views.editar_paciente, name='editar_paciente'),
]