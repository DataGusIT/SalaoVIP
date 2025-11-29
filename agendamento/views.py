from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.forms import modelformset_factory
from .models import Agendamento, HorarioTrabalho, Servico, Portfolio
from .forms import AgendamentoForm
from django.http import JsonResponse
from datetime import datetime, timedelta, time
from django.utils.timezone import make_aware 

# IMPORTAÇÃO DA FUNÇÃO DE NOTIFICAÇÃO
from notificacoes.utils import criar_notificacao

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
                
                # --- NOTIFICAÇÃO: AVISA O PROFISSIONAL ---
                msg_prof = f"Novo agendamento: {request.user.first_name or request.user.username} marcou {agendamento.servico.nome} para {agendamento.data_hora_inicio.strftime('%d/%m às %H:%M')}."
                criar_notificacao(agendamento.profissional, msg_prof, link='/agendamento/meus-agendamentos/')
                # -----------------------------------------

                messages.success(request, 'Agendamento realizado com sucesso!')
                return redirect('listar_agendamentos')
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

    # --- 1. CONFIGURAÇÃO DO FILTRO (DATA INICIO E FIM) ---
    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')

    # Se vierem datas na URL, usa elas. Se não, usa "Hoje" como padrão.
    if data_inicio_str and data_fim_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
            data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
        except ValueError:
            data_inicio = data_fim = hoje
    else:
        data_inicio = data_fim = hoje

    # --- 2. LÓGICA VISUAL DO BOTÃO ATIVO ---
    filtro_selecionado = 'personalizado'
    
    if data_inicio == hoje and data_fim == hoje:
        filtro_selecionado = 'hoje'
    # Verifica se é "Últimos 7 dias" (Hoje - 7 até Hoje)
    elif data_inicio == (hoje - timedelta(days=7)) and data_fim == hoje:
        filtro_selecionado = 'semana'
    # Verifica se é o mês atual (Dia 1 até fim do mês)
    elif data_inicio.day == 1 and data_fim.day > 27: 
        filtro_selecionado = 'mes'

    # --- 3. BUSCA NO BANCO DE DADOS (KPIs e TABELA) ---
    # Busca agendamentos dentro do intervalo selecionado
    agenda_periodo = Agendamento.objects.filter(
        profissional=request.user,
        data_hora_inicio__date__range=[data_inicio, data_fim]
    ).order_by('data_hora_inicio')

    # KPI: Faturamento do período (Soma apenas os CONCLUÍDOS)
    faturamento = agenda_periodo.filter(status='CONCLUIDO').aggregate(Sum('servico__preco'))['servico__preco__sum'] or 0

    # KPI: Total de atendimentos concluídos no período
    atendimentos_periodo = agenda_periodo.filter(status='CONCLUIDO').count()
    
    # KPI: Total geral na agenda (agendados + concluídos + cancelados) no período
    total_agendados = agenda_periodo.count()

    # --- 4. AGENDAMENTOS FUTUROS (ACCORDION) ---
    # Sempre mostra o que vem pela frente (Amanhã em diante), independente do filtro
    agenda_futura = Agendamento.objects.filter(
        profissional=request.user,
        data_hora_inicio__date__gt=hoje
    ).order_by('data_hora_inicio')

    context = {
        'agenda_periodo': agenda_periodo, # Nome usado na tabela principal
        'agenda_futura': agenda_futura,   # Nome usado no accordion
        'faturamento': faturamento,
        'atendimentos_periodo': atendimentos_periodo,
        'total_agendados': total_agendados,
        'hoje': hoje,
        # Dados para manter o filtro preenchido e o botão aceso
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'filtro_selecionado': filtro_selecionado,
        'filtro_ativo': data_inicio != hoje or data_fim != hoje
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
        
        # --- NOTIFICAÇÃO: SE O PROFISSIONAL CANCELAR, AVISA O CLIENTE ---
        if novo_status == 'CANCELADO':
            msg_cli = f"Atenção: Seu agendamento de {agendamento.data_hora_inicio.strftime('%d/%m às %H:%M')} foi cancelado pelo profissional."
            criar_notificacao(agendamento.cliente, msg_cli)
        # ---------------------------------------------------------------

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

# agendamento/views.py

def get_horarios_disponiveis(request):
    profissional_id = request.GET.get('profissional_id')
    data_str = request.GET.get('data')
    servico_id = request.GET.get('servico_id')

    print(f"--- DEBUG AGENDA ---")
    print(f"Recebido: Prof={profissional_id}, Data={data_str}, Servico={servico_id}")

    # Validação inicial
    if not all([profissional_id, data_str, servico_id]):
        print("ERRO: Faltando parâmetros.")
        return JsonResponse({'horarios': []})

    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        dia_semana = data_obj.weekday()
        print(f"Dia da semana: {dia_semana} (0=Seg, 6=Dom)")
    except ValueError:
        print("ERRO: Formato de data inválido.")
        return JsonResponse({'horarios': []})

    # 1. Busca Serviço
    try:
        servico = Servico.objects.get(id=servico_id)
        duracao = servico.duracao_minutos
        print(f"Serviço encontrado: {servico.nome}, Duração: {duracao}min")
    except Servico.DoesNotExist:
        print("ERRO: Serviço não encontrado.")
        return JsonResponse({'horarios': [], 'erro': 'Serviço inválido'})

    # 2. Busca Horário de Trabalho
    try:
        horario_config = HorarioTrabalho.objects.get(
            profissional_id=profissional_id, 
            dia_semana=dia_semana
        )
        print(f"Horário Config: {horario_config.hora_inicio} às {horario_config.hora_fim} | Folga: {horario_config.folga}")
    except HorarioTrabalho.DoesNotExist:
        print("ERRO: Sem configuração de horário para este dia.")
        return JsonResponse({'horarios': [], 'erro': 'Profissional não atende neste dia.'})

    if horario_config.folga:
        print("ERRO: Dia de folga.")
        return JsonResponse({'horarios': [], 'erro': 'Dia de folga.'})

    # 3. Gera slots
    slots_disponiveis = []
    
    # Datas com horário combinados (Naive - sem fuso horário para cálculo matemático)
    hora_atual = datetime.combine(data_obj, horario_config.hora_inicio)
    hora_fim_trab = datetime.combine(data_obj, horario_config.hora_fim)
    
    almoco_inicio = datetime.combine(data_obj, horario_config.almoco_inicio) if horario_config.almoco_inicio else None
    almoco_fim = datetime.combine(data_obj, horario_config.almoco_fim) if horario_config.almoco_fim else None

    # Busca agendamentos (Aware - com fuso horário)
    agendamentos = Agendamento.objects.filter(
        profissional_id=profissional_id,
        data_hora_inicio__date=data_obj,
        status='AGENDADO'
    )
    print(f"Agendamentos já existentes no dia: {agendamentos.count()}")

    # Loop de slots (Intervalo de 30 min para início)
    step = 30 
    
    while hora_atual + timedelta(minutes=duracao) <= hora_fim_trab:
        hora_termino_servico = hora_atual + timedelta(minutes=duracao)
        
        # --- Validações ---
        motivo_bloqueio = None

        # A. Almoço (Logica Naive vs Naive)
        if almoco_inicio and almoco_fim:
            if (hora_atual < almoco_fim) and (hora_termino_servico > almoco_inicio):
                motivo_bloqueio = "Almoço"

        # B. Conflitos (Lógica Aware vs Aware)
        if not motivo_bloqueio:
            slot_inicio_aware = make_aware(hora_atual)
            slot_fim_aware = make_aware(hora_termino_servico)
            
            for agendamento in agendamentos:
                # Se slot começa antes de terminar o agendamento E termina depois de começar o agendamento
                if (slot_inicio_aware < agendamento.data_hora_fim) and (slot_fim_aware > agendamento.data_hora_inicio):
                    motivo_bloqueio = f"Conflito agenda ({agendamento.data_hora_inicio.time()})"
                    break
        
        # C. Passado (Não deixar agendar para trás se for hoje)
        if not motivo_bloqueio:
            agora = timezone.now()
            # Se for hoje e o horário já passou
            if data_obj == agora.date() and make_aware(hora_atual) < agora:
                 motivo_bloqueio = "Horário já passou"

        # Adiciona ou Loga erro
        if not motivo_bloqueio:
            slots_disponiveis.append(hora_atual.strftime("%H:%M"))
        # else:
            # print(f"Slot {hora_atual.time()} bloqueado por: {motivo_bloqueio}") 

        hora_atual += timedelta(minutes=step)

    print(f"Total slots livres: {len(slots_disponiveis)}")
    return JsonResponse({'horarios': slots_disponiveis})

# Precisamos também de uma API para filtrar serviços pelo profissional
def api_get_servicos_por_profissional(request, profissional_id):
    servicos = Servico.objects.filter(profissional_id=profissional_id, ativo=True).values('id', 'nome', 'preco', 'duracao_minutos')
    return JsonResponse({'servicos': list(servicos)})


@login_required
def gerenciar_servicos(request):
    if request.user.tipo != 'CABELEIREIRO':
        return redirect('home')
        
    ServicoFormSet = modelformset_factory(Servico, fields=('nome', 'preco', 'duracao_minutos', 'ativo'), extra=1, can_delete=True)
    
    if request.method == 'POST':
        formset = ServicoFormSet(request.POST, queryset=Servico.objects.filter(profissional=request.user))
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.profissional = request.user
                instance.save()
            # Deletar os marcados para exclusão
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, "Serviços atualizados!")
            return redirect('gerenciar_servicos')
    else:
        formset = ServicoFormSet(queryset=Servico.objects.filter(profissional=request.user))

    return render(request, 'agendamento/gerenciar_servicos.html', {'formset': formset})

@login_required
def upload_foto_portfolio(request):
    if request.method == 'POST' and request.FILES.get('imagem_portfolio'):
        Portfolio.objects.create(
            profissional=request.user,
            imagem=request.FILES['imagem_portfolio'],
            descricao=request.POST.get('descricao', 'Trabalho realizado')
        )
        messages.success(request, "Foto adicionada ao portfólio!")
    
    return redirect('editar_perfil')

@login_required
def deletar_foto_portfolio(request, foto_id):
    foto = get_object_or_404(Portfolio, id=foto_id, profissional=request.user)
    foto.delete()
    messages.success(request, "Foto removida.")
    return redirect('editar_perfil')

@login_required
def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)

    # 1. Verifica se o agendamento pertence ao usuário logado
    if agendamento.cliente != request.user:
        messages.error(request, "Você não tem permissão para isso.")
        return redirect('listar_agendamentos')

    # 2. Regra das 2 horas
    if not agendamento.pode_cancelar:
        messages.error(request, "Faltam menos de 2h. Entre em contato com o profissional.")
        return redirect('listar_agendamentos')

    # 3. Cancela
    agendamento.status = 'CANCELADO'
    agendamento.save()
    
    # --- NOTIFICAÇÃO: AVISA O PROFISSIONAL ---
    msg_canc = f"Cancelamento: {request.user.first_name or request.user.username} cancelou o horário de {agendamento.data_hora_inicio.strftime('%d/%m às %H:%M')}."
    criar_notificacao(agendamento.profissional, msg_canc)
    # -----------------------------------------

    messages.success(request, "Agendamento cancelado com sucesso.")
    return redirect('listar_agendamentos')