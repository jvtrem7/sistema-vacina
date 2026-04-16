from django.shortcuts import render, redirect
from .models import Vacina, Paciente, Estoque
from .forms import PacienteForm
from .forms import PacienteForm, VacinaForm
from django.shortcuts import get_object_or_404
from .models import PostoSaude
from django.contrib.auth.decorators import login_required
from .forms import EstoqueForm
from django.shortcuts import redirect, render

@login_required
def home(request):
    todas_vacinas = Vacina.objects.all().order_by('-data_aplicacao')
    total_pacientes = Paciente.objects.count()
    todos_pacientes = Paciente.objects.all()
    return render(request, 'vacinas/index.html', {
        'vacinas': todas_vacinas,
        'total_pacientes': total_pacientes,
        'pacientes': todos_pacientes
    })
@login_required
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
@login_required
def registrar_dose(request):
    if request.method == 'POST':
        form = VacinaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = VacinaForm()
    return render(request, 'vacinas/registrar_dose.html', {'form': form})
@login_required
def listar_pacientes(request):
    pacientes = Paciente.objects.all().order_by('nome')
    return render(request, 'vacinas/listar_pacientes.html', {'pacientes': pacientes})
@login_required
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

def caderneta_paciente(request):
    cpf_busca = request.GET.get('cpf')
    vacinas = None
    paciente = None
    
    if cpf_busca:
        paciente = Paciente.objects.filter(cpf=cpf_busca).first()
        if paciente:
            vacinas = Vacina.objects.filter(paciente=paciente).order_by('-data_aplicacao')
            
    return render(request, 'vacinas/caderneta.html', {
        'vacinas': vacinas,
        'paciente': paciente,
        'cpf_busca': cpf_busca
    })

def listar_postos(request):
    from .models import PostoSaude
    postos = PostoSaude.objects.all()
    return render(request, 'vacinas/postos.html', {'postos': postos})

def index_escolha(request):
    return render(request, 'vacinas/index_escolha.html')

def listar_estoque(request):
    itens = Estoque.objects.all()
    return render(request, 'vacinas/estoque.html', {'itens': itens})
def cadastrar_estoque(request):
    if request.method == 'POST':
        form = EstoqueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_estoque')
    else:
        form = EstoqueForm()
    return render(request, 'vacinas/cadastrar_estoque.html', {'form': form})