from django.urls import path
from . import views

urlpatterns = [
    path('novo/', views.novo_agendamento, name='novo_agendamento'),
    path('meus-agendamentos/', views.listar_agendamentos, name='listar_agendamentos'),
    path('status/<int:agendamento_id>/<str:novo_status>/', views.mudar_status, name='mudar_status'),
    # Rota para salvar a nota
    path('concluir/<int:agendamento_id>/', views.concluir_agendamento, name='concluir_agendamento'),
    
    # Rota API para pegar o histórico via Javascript
    path('api/historico/<int:cliente_id>/', views.obter_historico_cliente, name='api_historico_cliente'),

]