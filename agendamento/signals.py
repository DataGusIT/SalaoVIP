from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from .models import HorarioTrabalho

@receiver(post_save, sender=User)
def criar_horario_padrao(sender, instance, created, **kwargs):
    # Se o usuário for criado ou atualizado e for CABELEIREIRO
    if instance.tipo == 'CABELEIREIRO':
        # Verifica se já tem horários. Se não tiver, cria os 7 dias.
        if not HorarioTrabalho.objects.filter(profissional=instance).exists():
            for dia in range(7): # 0 a 6
                # Por padrão, Sábado e Domingo (5 e 6) são folga? Vamos deixar só Domingo.
                eh_folga = True if dia == 6 else False
                HorarioTrabalho.objects.create(
                    profissional=instance,
                    dia_semana=dia,
                    folga=eh_folga
                )