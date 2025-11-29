from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from .models import Agendamento
from .forms import AgendamentoForm


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