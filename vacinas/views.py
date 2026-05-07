import csv
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vacina, Paciente, Estoque, PostoSaude
from .forms import PacienteForm, VacinaForm, EstoqueForm
from django.http import HttpResponse
from django.db.models.functions import Replace
from django.db.models import Value

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
    return render(request, 'vacinas/cadastro_paciente.html', {'form': form, 'editando': True})

def caderneta_paciente(request):
    cpf_busca = request.GET.get('cpf')
    vacinas = None
    paciente = None
    if cpf_busca:
        paciente = Paciente.objects.filter(cpf=cpf_busca).first()
        if paciente:
            vacinas = Vacina.objects.filter(paciente=paciente).order_by('-data_aplicacao')
    return render(request, 'vacinas/caderneta.html', {'vacinas': vacinas, 'paciente': paciente, 'cpf_busca': cpf_busca})

def index_escolha(request):
    return render(request, 'vacinas/index_escolha.html')

@login_required
def listar_estoque(request):
    itens = Estoque.objects.all()
    return render(request, 'vacinas/estoque.html', {'itens': itens})

@login_required
def cadastrar_estoque(request):
    if request.method == 'POST':
        form = EstoqueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_estoque')
    else:
        form = EstoqueForm()
    return render(request, 'vacinas/cadastrar_estoque.html', {'form': form})

def consulta_cep_postos(request):
    cep_digitado = request.GET.get('cep')
    postos_encontrados = PostoSaude.objects.none()

    if cep_digitado:
        cep_limpo = cep_digitado.replace("-", "").replace(" ", "")
        
        postos_encontrados = PostoSaude.objects.annotate(
            cep_sem_hifen=Replace('cep', Value('-'), Value(''))
        ).filter(cep_sem_hifen__icontains=cep_limpo)

       
        if not postos_encontrados.exists():
            url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    dados = response.json()
                    bairro_detectado = dados.get('bairro')
                    
                    if bairro_detectado:
                        postos_encontrados = PostoSaude.objects.filter(bairro__icontains=bairro_detectado)
            except:
                pass 

    return render(request, 'vacinas/postos.html', {
        'postos': postos_encontrados,
        'bairro_localizado': bairro_detectado,
        'cep_pesquisado': cep_digitado
    })

@login_required
def exportar_dados_csv(request):
 
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="relatorio_vacinas_saquarema.csv"'

    response.write(u'\ufeff'.encode('utf8')) 
    
    writer = csv.writer(response, delimiter=';')

    writer.writerow(['Paciente', 'CPF', 'Vacina', 'Data de Aplicação', 'Posto de Saúde'])

    vacinacoes = Vacina.objects.all().select_related('paciente', 'posto')

    for v in vacinacoes:
        writer.writerow([
            v.paciente.nome,
            v.paciente.cpf,
            v.item_estoque.nome_vacina if v.item_estoque else "N/A",
            v.data_aplicacao.strftime('%d/%m/%Y %H:%M'),
            v.item_estoque.posto.nome if v.item_estoque and v.item_estoque.posto else "N/A"
        ])

    return response