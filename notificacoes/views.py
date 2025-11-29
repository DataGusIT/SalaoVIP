from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notificacao

@login_required
def listar_notificacoes(request):
    notificacoes = request.user.notificacoes.all()
    
    # Marca todas como lidas ao abrir a página (simples e eficaz)
    # Ou poderíamos marcar uma por uma ao clicar, mas assim limpa o sininho rápido
    request.user.notificacoes.filter(lida=False).update(lida=True)
    
    return render(request, 'notificacoes/listar.html', {'notificacoes': notificacoes})