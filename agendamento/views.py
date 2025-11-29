from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.forms import modelformset_factory
from .models import Agendamento, HorarioTrabalho
from .forms import AgendamentoForm
from django.http import JsonResponse
from datetime import datetime, timedelta, time
from django.utils.timezone import make_aware 


@login_required
def novo_agendamento(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.cliente = request.user # Associa o cliente logado automaticamente
            
            try:
                # O full_clean() chama o clean() do model onde está nossa validação de horário
                agendamento.full_clean() 
                agendamento.save()
                messages.success(request, 'Agendamento realizado com sucesso!')
                return redirect('listar_agendamentos') # Vamos criar essa rota já já
            except Exception as e:
                # Se der erro de validação (horário ocupado), aparece aqui
                messages.error(request, e)
    else:
        form = AgendamentoForm()

    return render(request, 'agendamento/novo_agendamento.html', {'form': form})

@login_required
def listar_agendamentos(request):
    # SE FOR CABELEIREIRO, VAI PARA O DASHBOARD NOVO
    if request.user.tipo == 'CABELEIREIRO':
        return dashboard_profissional(request)
    
    # SE FOR CLIENTE, CONTINUA COM O HISTÓRICO PADRÃO
    agendamentos = request.user.agendamentos_cliente.all().order_by('-data_hora_inicio')
    return render(request, 'agendamento/listar_agendamentos.html', {
        'agendamentos': agendamentos
    })

@login_required
def dashboard_profissional(request):
    # Garante que só cabeleireiros acessam
    if request.user.tipo != 'CABELEIREIRO':
        return redirect('home')

    hoje = timezone.localdate() 
    
     # 1. Agendamentos de HOJE
    agenda_hoje = Agendamento.objects.filter(
        profissional=request.user,
        data_hora_inicio__date=hoje
    ).order_by('data_hora_inicio')

    # 2. Agendamentos FUTUROS
    agenda_futura = Agendamento.objects.filter(
        profissional=request.user,
        data_hora_inicio__date__gt=hoje
    ).order_by('data_hora_inicio')

    # 3. Faturamento do Mês (Soma preços de agendamentos CONCLUÍDOS)
    mes_atual = timezone.now().month
    faturamento = Agendamento.objects.filter(
        profissional=request.user,
        status='CONCLUIDO',
        data_hora_inicio__month=mes_atual
    ).aggregate(Sum('servico__preco'))['servico__preco__sum'] or 0

    # 4. Clientes atendidos hoje (Concluídos)
    atendimentos_hoje = agenda_hoje.filter(status='CONCLUIDO').count()

    context = {
        'agenda_hoje': agenda_hoje,
        'agenda_futura': agenda_futura,
        'faturamento': faturamento,
        'atendimentos_hoje': atendimentos_hoje,
        'hoje': hoje,
    }
    
    return render(request, 'agendamento/dashboard_profissional.html', context)

@login_required
def mudar_status(request, agendamento_id, novo_status):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)

    # Segurança: Só o profissional dono do agendamento pode mexer
    if request.user != agendamento.profissional:
        messages.error(request, "Você não tem permissão para alterar este agendamento.")
        return redirect('listar_agendamentos')

    if novo_status in ['CONCLUIDO', 'CANCELADO', 'NAO_COMPARECEU']:
        agendamento.status = novo_status
        agendamento.save()
        messages.success(request, f"Status atualizado para {agendamento.get_status_display()}")
    
    return redirect('listar_agendamentos')

@login_required
def concluir_agendamento(request, agendamento_id):
    if request.method == 'POST':
        agendamento = get_object_or_404(Agendamento, id=agendamento_id)
        
        # Segurança
        if request.user != agendamento.profissional:
            messages.error(request, "Acesso negado.")
            return redirect('listar_agendamentos')
        
        # Salva a nota e muda o status
        nota = request.POST.get('anotacoes')
        agendamento.anotacoes = nota
        agendamento.status = 'CONCLUIDO'
        agendamento.save()
        
        messages.success(request, "Atendimento concluído e prontuário salvo!")
        return redirect('listar_agendamentos')

@login_required
def obter_historico_cliente(request, cliente_id):
    """
    Retorna um JSON com os cortes passados desse cliente.
    Usaremos isso para mostrar no Modal de Histórico sem recarregar a página.
    """
    cortes_passados = Agendamento.objects.filter(
        cliente_id=cliente_id,
        profissional=request.user, # Só mostra o que esse barbeiro fez (opcional)
        status='CONCLUIDO'
    ).order_by('-data_hora_inicio')[:5] # Pega os últimos 5
    
    data = []
    for corte in cortes_passados:
        data.append({
            'data': corte.data_hora_inicio.strftime('%d/%m/%Y'),
            'servico': corte.servico.nome,
            'nota': corte.anotacoes or "Sem anotações."
        })
    
    return JsonResponse({'historico': data})

@login_required
def configurar_horarios(request):
    if request.user.tipo != 'CABELEIREIRO':
        return redirect('home')

    # Truque: Se não tiver horários (usuário antigo), cria agora
    if not HorarioTrabalho.objects.filter(profissional=request.user).exists():
        for dia in range(7):
            HorarioTrabalho.objects.create(profissional=request.user, dia_semana=dia, folga=(dia==6))

    # Cria um formulário que edita Múltiplas linhas
    HorarioFormSet = modelformset_factory(
        HorarioTrabalho,
        fields=('hora_inicio', 'hora_fim', 'almoco_inicio', 'almoco_fim', 'folga'),
        extra=0 # Não criar linhas novas, só editar as 7 existentes
    )

    if request.method == 'POST':
        formset = HorarioFormSet(request.POST, queryset=HorarioTrabalho.objects.filter(profissional=request.user))
        if formset.is_valid():
            formset.save()
            messages.success(request, "Horários de trabalho atualizados!")
            return redirect('configurar_horarios')
        else:
            messages.error(request, "Erro ao salvar. Verifique os horários.")
    else:
        formset = HorarioFormSet(queryset=HorarioTrabalho.objects.filter(profissional=request.user))

    return render(request, 'agendamento/configurar_horarios.html', {'formset': formset})

def get_horarios_disponiveis(request):
    profissional_id = request.GET.get('profissional_id')
    data_str = request.GET.get('data') # Formato YYYY-MM-DD
    
    if not profissional_id or not data_str:
        return JsonResponse({'horarios': []})

    # Converte string para data
    data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
    dia_semana = data_obj.weekday()

    # 1. Verifica se trabalha neste dia
    try:
        horario_config = HorarioTrabalho.objects.get(
            profissional_id=profissional_id, 
            dia_semana=dia_semana
        )
    except HorarioTrabalho.DoesNotExist:
        return JsonResponse({'horarios': [], 'erro': 'Profissional não atende neste dia da semana.'})

    if horario_config.folga:
        return JsonResponse({'horarios': [], 'erro': 'Dia de folga.'})

    # 2. Gera todos os slots possíveis (de 30 em 30 min)
    # Nota: Idealmente o intervalo viria da duração do serviço, mas vamos fixar 30min por simplicidade agora
    intervalo = 30 
    slots_possiveis = []
    
    hora_atual = datetime.combine(data_obj, horario_config.hora_inicio)
    hora_fim_trab = datetime.combine(data_obj, horario_config.hora_fim)
    
    # Prepara horários de almoço
    almoco_inicio = datetime.combine(data_obj, horario_config.almoco_inicio) if horario_config.almoco_inicio else None
    almoco_fim = datetime.combine(data_obj, horario_config.almoco_fim) if horario_config.almoco_fim else None

    # Busca agendamentos já existentes nesse dia
    agendamentos = Agendamento.objects.filter(
        profissional_id=profissional_id,
        data_hora_inicio__date=data_obj,
        status='AGENDADO'
    )

    while hora_atual + timedelta(minutes=intervalo) <= hora_fim_trab:
        slot_fim = hora_atual + timedelta(minutes=intervalo)
        
        # Validação 1: Almoço
        no_almoco = False
        if almoco_inicio and almoco_fim:
            # Se o slot começa dentro do almoço OU termina dentro dele
            if (hora_atual >= almoco_inicio and hora_atual < almoco_fim) or \
               (slot_fim > almoco_inicio and slot_fim <= almoco_fim):
                no_almoco = True
        
        # Validação 2: Conflito com Agendamentos
        ocupado = False
        for agendamento in agendamentos:
            # Lógica de overlap
            # Make aware garante que estamos comparando fusos certos
            start_aware = make_aware(hora_atual)
            end_aware = make_aware(slot_fim)
            
            if start_aware < agendamento.data_hora_fim and end_aware > agendamento.data_hora_inicio:
                ocupado = True
                break
        
        # Se passou nos testes, adiciona
        if not no_almoco and not ocupado:
            slots_possiveis.append(hora_atual.strftime("%H:%M"))
            
        hora_atual += timedelta(minutes=intervalo)

    return JsonResponse({'horarios': slots_possiveis})