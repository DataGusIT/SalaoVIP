from django.contrib import admin
from .models import Servico, Agendamento

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'duracao_minutos', 'ativo']
    search_fields = ['nome']

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'profissional', 'servico', 'data_hora_inicio', 'data_hora_fim', 'status']
    list_filter = ['status', 'profissional', 'data_hora_inicio']
    # Não permitimos editar data_hora_fim pois é automático
    readonly_fields = ['data_hora_fim']