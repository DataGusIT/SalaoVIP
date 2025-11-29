from .models import Notificacao

def contador_notificacoes(request):
    if request.user.is_authenticated:
        # Conta quantas não foram lidas
        count = Notificacao.objects.filter(destinatario=request.user, lida=False).count()
        return {'notificacoes_nao_lidas': count}
    return {'notificacoes_nao_lidas': 0}