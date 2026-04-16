from django.shortcuts import render, redirect
from .models import Vacina, Paciente
from .forms import PacienteForm
from .forms import PacienteForm, VacinaForm
from django.shortcuts import get_object_or_404


def home(request):
    todas_vacinas = Vacina.objects.all().order_by('-data_aplicacao')
    total_pacientes = Paciente.objects.count()
    todos_pacientes = Paciente.objects.all()
    return render(request, 'vacinas/index.html', {
        'vacinas': todas_vacinas,
        'total_pacientes': total_pacientes,
        'pacientes': todos_pacientes
    })

def cadastrar_paciente(request):
    if request.method == 'POST': 
        form = PacienteForm(request.POST)
        if form.is_valid():     
            form.save()         
            return redirect('home') 
        else:
            print(form.errors)  
    else:
        form = PacienteForm()
    return render(request, 'vacinas/cadastro_paciente.html', {'form': form})

def registrar_dose(request):
    if request.method == 'POST':
        form = VacinaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = VacinaForm()
    return render(request, 'vacinas/registrar_dose.html', {'form': form})

def listar_pacientes(request):
    pacientes = Paciente.objects.all().order_by('nome')
    return render(request, 'vacinas/listar_pacientes.html', {'pacientes': pacientes})

def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    form = PacienteForm(request.POST or None, instance=paciente) 
    
    if form.is_valid():
        form.save()
        return redirect('listar_pacientes')
        
    return render(request, 'vacinas/cadastro_paciente.html', {
        'form': form,
        'editando': True 
    })