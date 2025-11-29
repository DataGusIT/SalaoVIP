from django.urls import path
from . import views

urlpatterns = [
    path('novo/', views.novo_agendamento, name='novo_agendamento'),
    path('meus-agendamentos/', views.listar_agendamentos, name='listar_agendamentos'),
    path('status/<int:agendamento_id>/<str:novo_status>/', views.mudar_status, name='mudar_status'),

]