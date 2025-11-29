from django.urls import path
from . import views

urlpatterns = [
    path('novo/', views.novo_agendamento, name='novo_agendamento'),
    path('meus-agendamentos/', views.listar_agendamentos, name='listar_agendamentos'),
    
    # Rota para mudar status (já existia)
    path('status/<int:agendamento_id>/<str:novo_status>/', views.mudar_status, name='mudar_status'),
    
    # Rota para concluir com nota (já existia)
    path('concluir/<int:agendamento_id>/', views.concluir_agendamento, name='concluir_agendamento'),
    
    # APIs (já existiam)
    path('api/historico/<int:cliente_id>/', views.obter_historico_cliente, name='api_historico_cliente'),
    path('api/horarios-disponiveis/', views.get_horarios_disponiveis, name='api_horarios_disponiveis'),
    path('api/servicos/<int:profissional_id>/', views.api_get_servicos_por_profissional, name='api_servicos'),

    # --- AS NOVAS ROTAS QUE FALTAVAM ---
    path('configurar-horarios/', views.configurar_horarios, name='configurar_horarios'),
    path('meus-servicos/', views.gerenciar_servicos, name='gerenciar_servicos'), # <--- ESSA AQUI RESOLVE O ERRO
    
    # Rotas de Portfolio
    path('portfolio/upload/', views.upload_foto_portfolio, name='upload_foto_portfolio'),
    path('portfolio/delete/<int:foto_id>/', views.deletar_foto_portfolio, name='deletar_foto_portfolio'),
]