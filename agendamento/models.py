from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import timedelta

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    duracao_minutos = models.PositiveIntegerField(help_text="Duração em minutos")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"

class Agendamento(models.Model):
    STATUS_CHOICES = (
        ('AGENDADO', 'Agendado'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
        ('NAO_COMPARECEU', 'Não Compareceu'),
    )

    # --- DEFINIÇÃO DOS CAMPOS (Eles precisam estar aqui!) ---
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agendamentos_cliente')
    profissional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agendamentos_profissional')
    servico = models.ForeignKey(Servico, on_delete=models.SET_NULL, null=True)
    
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField(editable=False, blank=True, null=True) 
    anotacoes = models.TextField(blank=True, null=True, help_text="Campo exclusivo para o profissional (Prontuário)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADO')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_hora_inicio']
    
    def __str__(self):
        return f"{self.cliente} - {self.servico} - {self.data_hora_inicio}"

    # --- MÉTODOS DE INTELIGÊNCIA ---

    def calcular_fim(self):
        """Método auxiliar para calcular o horário final"""
        if self.servico and self.data_hora_inicio:
            return self.data_hora_inicio + timedelta(minutes=self.servico.duracao_minutos)
        return None

    def clean(self):
        # 1. Garantir que temos o horário final calculado ANTES de validar
        if not self.data_hora_fim:
            self.data_hora_fim = self.calcular_fim()

        # Se mesmo calculando, faltar dados, paramos aqui
        if not self.data_hora_fim or not self.data_hora_inicio:
            return

        # 2. Validação de Inteligência (Overbooking)
        conflitos = Agendamento.objects.filter(
            profissional=self.profissional,
            status='AGENDADO',
            data_hora_inicio__lt=self.data_hora_fim, 
            data_hora_fim__gt=self.data_hora_inicio
        ).exclude(id=self.id)

        if conflitos.exists():
            raise ValidationError(f"O profissional {self.profissional} já tem um agendamento neste horário.")

    def save(self, *args, **kwargs):
        # Garante o cálculo ao salvar também
        self.data_hora_fim = self.calcular_fim()
        super().save(*args, **kwargs)