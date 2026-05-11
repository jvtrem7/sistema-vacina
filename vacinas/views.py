import csv
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vacina, Paciente, Estoque, PostoSaude, Agendamento
from .forms import PacienteForm, VacinaForm, EstoqueForm
from django.http import HttpResponse
from django.db.models import Q
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages  
from .models import Agendamento     
from .forms import VacinaForm   
from django.contrib import messages    

@login_required
def home(request):
    todas_vacinas = Vacina.objects.all().select_related('paciente', 'item_estoque__posto').order_by('-data_aplicacao')
    total_pacientes = Paciente.objects.count()
    context = {
        'total_pacientes': total_pacientes,}
    return render(request, 'vacinas/index.html', {
        'vacinas': todas_vacinas,
        'total_pacientes': total_pacientes,
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
            # Isso vai imprimir o erro no terminal do seu PC para você ver o que é
            print(form.errors) 
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

def portal_boas_vindas(request):
    return render(request, 'vacinas/portal_boas_vindas.html')

def caderneta_paciente(request):
    cpf = request.GET.get('cpf')
    paciente = None
    doses = [] # Criamos a lista de doses vazia por padrão
    
    if cpf:
        paciente = Paciente.objects.filter(cpf=cpf).first()
        if paciente:
    
            doses = Vacina.objects.filter(paciente=paciente).select_related('item_estoque__posto').order_by('-data_aplicacao')
    
    return render(request, 'vacinas/caderneta.html', {
        'paciente': paciente,
        'doses': doses, 
        'busca_ativa': bool(cpf)
    })

def index_escolha(request):
    return render(request, 'vacinas/index_escolha.html')

@login_required
def listar_estoque(request):
    # Exibe os itens de estoque e o posto ao qual pertencem
    itens = Estoque.objects.all().select_related('posto')
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

def busca_postos(request):
    """
    Função unificada para busca de postos por CEP ou Bairro (ViaCEP)
    """
    cep_digitado = request.GET.get('cep', '').strip()
    postos_encontrados = PostoSaude.objects.none()
    bairro_detectado = None 

    if cep_digitado:
        cep_limpo = cep_digitado.replace("-", "").replace(" ", "").replace(".", "")
        
        # 1. Busca direta no banco pelo CEP
        postos_encontrados = PostoSaude.objects.filter(
            Q(cep=cep_digitado) | Q(cep=cep_limpo)
        )

        # 2. Se não achou, consulta o ViaCEP para identificar o bairro e buscar por ele
        if not postos_encontrados.exists():
            url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    dados = response.json()
                    if 'erro' not in dados:
                        bairro_detectado = dados.get('bairro')
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

    writer.writerow(['Paciente', 'CPF', 'Vacina', 'Lote', 'Data de Aplicação', 'Posto de Saúde'])

    # Otimização de consulta com select_related
    vacinacoes = Vacina.objects.all().select_related('paciente', 'item_estoque__posto')

    for v in vacinacoes:
        writer.writerow([
            v.paciente.nome,
            v.paciente.cpf,
            v.nome_vacina,
            v.lote,
            v.data_aplicacao.strftime('%d/%m/%Y %H:%M'),
            v.posto.nome if v.posto else "N/A"
        ])

    return response

def carregar_vacinas_posto(request):
    posto_id = request.GET.get('posto_id')
    vacinas = Estoque.objects.filter(posto_id=posto_id, quantidade_atual__gt=0).values('id', 'nome_vacina', 'lote')
    return JsonResponse(list(vacinas), safe=False)


def agendar_vacina(request):
    # Definimos a variável no topo para ela sempre existir
    postos = PostoSaude.objects.all()
    
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        item_id = request.POST.get('item_estoque')
        data_hora = request.POST.get('data_hora')
        
        paciente = Paciente.objects.filter(cpf=cpf).first()
        
        if not paciente:
            messages.error(request, 'CPF não encontrado. Faça seu cadastro primeiro.')
            return render(request, 'vacinas/agendar_vacina.html', {'postos': postos})

        try:
            with transaction.atomic():
                estoque = Estoque.objects.select_for_update().get(id=item_id)
                
                if (estoque.quantidade_atual - estoque.quantidade_reservada) > 0:
                    Agendamento.objects.create(
                        paciente=paciente,
                        item_estoque=estoque,
                        data_hora=data_hora,
                        status='pendente'
                    )
                    estoque.quantidade_reservada += 1
                    estoque.save()
                    
                    messages.success(request, "Agendamento realizado com sucesso!")
                    # Redirecionamos para a tela de escolha para garantir o funcionamento
                    return render(request, 'vacinas/agendar_vacina.html', {'postos': postos})
                else:
                    messages.error(request, "Não há doses disponíveis.")
        except Exception as e:
            messages.error(request, f"Erro no sistema: {e}")

    # Este retorno garante que o GET (carregamento inicial) funcione sem erro de 'postos'
    return render(request, 'vacinas/agendar_vacina.html', {'postos': postos})
            
    postos = PostoSaude.objects.all()
    return render(request, 'vacinas/agendar_vacina.html', {'postos': postos})

@login_required
def listar_agendamentos(request):
    agendamentos = Agendamento.objects.filter(status='pendente').select_related('paciente', 'item_estoque', 'item_estoque__posto').order_by('data_hora')
    
    return render(request, 'vacinas/listar_agendamentos.html', {'agendamentos': agendamentos})

def meus_agendamentos(request):
    agendamentos = None
    cpf_consultado = request.GET.get('cpf')

    if cpf_consultado:
        agendamentos = Agendamento.objects.filter(
            paciente__cpf=cpf_consultado
        ).order_by('-data_hora')

    return render(request, 'vacinas/meus_agendamentos.html', {
        'agendamentos': agendamentos,
        'cpf_consultado': cpf_consultado
    })

@login_required
def confirmar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    with transaction.atomic():
        estoque = agendamento.item_estoque
        if estoque.quantidade_atual > 0:
            estoque.quantidade_atual -= 1
            estoque.quantidade_reservada -= 1
            estoque.save()
            
            agendamento.status = 'concluido'
            agendamento.save()
            messages.success(request, f"Dose confirmada para {agendamento.paciente.nome}!")
        else:
            messages.error(request, "Estoque insuficiente!")
            
    return redirect('listar_agendamentos')

@login_required
def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    with transaction.atomic():
        estoque = agendamento.item_estoque
        # No cancelamento, a gente APENAS diminui a reserva
        # A quantidade_atual não muda porque a vacina não foi aplicada
        if estoque.quantidade_reservada > 0:
            estoque.quantidade_reservada -= 1
            estoque.save()
            
            agendamento.status = 'cancelado'
            agendamento.save()
            messages.warning(request, f"Agendamento de {agendamento.paciente.nome} cancelado.")
            
    return redirect('listar_agendamentos')

def historico_agendamentos(request):
    # Aqui pegamos todos que NÃO estão pendentes para ser o seu arquivo morto
    agendamentos = Agendamento.objects.exclude(status='pendente').order_by('-data_hora')
    return render(request, 'vacinas/historico_agendamentos.html', {'agendamentos': agendamentos})

def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    if request.method == 'POST':
        justificativa = request.POST.get('justificativa')
        
        with transaction.atomic():
            estoque = agendamento.item_estoque
            
            # Se estava concluído, devolvemos 1 para a quantidade atual
            if agendamento.status == 'concluido':
                estoque.quantidade_atual += 1
            # Se estava pendente, apenas removemos da reserva
            elif agendamento.status == 'pendente':
                estoque.quantidade_reservada -= 1
            
            estoque.save()
            
            agendamento.status = 'cancelado'
            agendamento.justificativa_cancelamento = justificativa
            agendamento.save()
            
            messages.warning(request, "Agendamento cancelado e estoque atualizado.")
            return redirect('listar_agendamentos')

    return render(request, 'vacinas/confirmar_cancelamento.html', {'agendamento': agendamento})