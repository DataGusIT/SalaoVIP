from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import timedelta

class Servico(models.Model):
    # Adicionamos o vínculo com o profissional
    profissional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='servicos')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    duracao_minutos = models.PositiveIntegerField(help_text="Duração em minutos")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} ({self.duracao_minutos} min) - {self.profissional.first_name}"
    
class Portfolio(models.Model):
    profissional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolio')
    imagem = models.ImageField(upload_to='portfolio/')
    descricao = models.CharField(max_length=200, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.profissional}"
    
class HorarioTrabalho(models.Model):
    DIAS_SEMANA = (
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    )

    profissional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='horarios_trabalho')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    
    hora_inicio = models.TimeField(default='09:00')
    hora_fim = models.TimeField(default='18:00')
    
    almoco_inicio = models.TimeField(default='12:00', blank=True, null=True)
    almoco_fim = models.TimeField(default='13:00', blank=True, null=True)
    
    folga = models.BooleanField(default=False)

    class Meta:
        # Garante que só exista uma regra por dia para cada profissional
        unique_together = ('profissional', 'dia_semana')
        ordering = ['dia_semana']

    def __str__(self):
        return f"{self.get_dia_semana_display()} - {self.profissional}"

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
        # ... (mantenha a lógica de cálculo de fim que já existia) ...
        if not self.data_hora_fim:
            self.data_hora_fim = self.calcular_fim()
            
        if not self.data_hora_fim or not self.data_hora_inicio:
            return

        # --- NOVA VALIDAÇÃO: HORÁRIO DE TRABALHO ---
        # 1. Descobre qual é o dia da semana da data escolhida (0=Seg, 6=Dom)
        dia_semana_agendado = self.data_hora_inicio.weekday()
        
        try:
            horario = HorarioTrabalho.objects.get(
                profissional=self.profissional, 
                dia_semana=dia_semana_agendado
            )
        except HorarioTrabalho.DoesNotExist:
            # Se o profissional não configurou horário, assumimos que não trabalha
            raise ValidationError(f"O profissional não configurou agenda para {self.data_hora_inicio.strftime('%A')}.")

        # 2. Verifica se é Folga
        if horario.folga:
            raise ValidationError("O profissional não trabalha neste dia.")

        # 3. Verifica se está dentro do horário comercial
        # Convertemos datetime para time para comparar apenas as horas
        hora_inicio_agendamento = self.data_hora_inicio.time()
        hora_fim_agendamento = self.data_hora_fim.time()

        if hora_inicio_agendamento < horario.hora_inicio or hora_fim_agendamento > horario.hora_fim:
            raise ValidationError(f"Fora do horário de expediente ({horario.hora_inicio.strftime('%H:%M')} às {horario.hora_fim.strftime('%H:%M')}).")

        # 4. Verifica intervalo de almoço (Se houver almoço configurado)
        if horario.almoco_inicio and horario.almoco_fim:
            # Se o corte começa DENTRO do almoço OU termina DENTRO do almoço
            comeca_no_almoco = horario.almoco_inicio <= hora_inicio_agendamento < horario.almoco_fim
            termina_no_almoco = horario.almoco_inicio < hora_fim_agendamento <= horario.almoco_fim
            
            # Ou se o corte "engole" o almoço inteiro (começa antes e termina depois)
            engole_almoco = hora_inicio_agendamento <= horario.almoco_inicio and hora_fim_agendamento >= horario.almoco_fim

            if comeca_no_almoco or termina_no_almoco or engole_almoco:
                raise ValidationError(f"Horário coincide com o intervalo de almoço ({horario.almoco_inicio.strftime('%H:%M')} às {horario.almoco_fim.strftime('%H:%M')}).")

        # --- FIM DA NOVA VALIDAÇÃO ---

        # 5. Verifica conflitos com outros agendamentos
        conflitos = Agendamento.objects.filter(
            profissional=self.profissional,
            data_hora_inicio__lt=self.data_hora_fim,
            data_hora_fim__gt=self.data_hora_inicio,
            status__in=['AGENDADO', 'CONCLUIDO']
        ).exclude(pk=self.pk)

        if conflitos.exists():
            raise ValidationError(f"O profissional {self.profissional} já tem um agendamento neste horário.")

    def save(self, *args, **kwargs):
        # Garante o cálculo ao salvar também
        self.data_hora_fim = self.calcular_fim()
        super().save(*args, **kwargs)