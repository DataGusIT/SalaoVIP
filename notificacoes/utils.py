from .models import Notificacao

def criar_notificacao(destinatario, mensagem, link=None):
    Notificacao.objects.create(
        destinatario=destinatario,
        mensagem=mensagem,
        link=link
    )