from django.db import models
from django.conf import settings

class Notificacao(models.Model):
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.CharField(max_length=255)
    lida = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True, null=True) # Para clicar e ir direto pro agendamento
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"Para {self.destinatario}: {self.mensagem}"