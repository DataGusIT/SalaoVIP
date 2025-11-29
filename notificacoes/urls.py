from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_notificacoes, name='listar_notificacoes'),
]