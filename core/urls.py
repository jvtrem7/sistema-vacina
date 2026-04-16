from django.contrib import admin
from django.urls import path
from vacinas.views import home 
from vacinas import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_escolha, name='index_escolha'),
    path('dashboard/', views.home, name='home'), 
    path('novo-paciente/', views.cadastrar_paciente, name='cadastrar_paciente'),
    path('registrar-dose/', views.registrar_dose, name='registrar_dose'),
    path('pacientes/', views.listar_pacientes, name='listar_pacientes'),
    path('editar-paciente/<int:pk>/', views.editar_paciente, name='editar_paciente'),
    path('caderneta/', views.caderneta_paciente, name='caderneta_paciente'),
    path('postos/', views.listar_postos, name='listar_postos'),
    path('login/', auth_views.LoginView.as_view(template_name='vacinas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('estoque/', views.listar_estoque, name='listar_estoque'),
    path('estoque/novo/', views.cadastrar_estoque, name='cadastrar_estoque'),
]