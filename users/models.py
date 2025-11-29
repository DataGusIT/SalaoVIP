from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    TYPE_CHOICES = (
        ('CLIENTE', 'Cliente'),
        ('CABELEIREIRO', 'Cabeleireiro'),
        ('ADMIN', 'Administrador'),
    )

    # Campos adicionais
    tipo = models.CharField(max_length=15, choices=TYPE_CHOICES, default='CLIENTE')
    telefone = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    
    # Adicione aqui outros campos globais se precisar (ex: data_nascimento)

    def __str__(self):
        return self.username