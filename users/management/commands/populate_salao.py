from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from agendamento.models import Servico, HorarioTrabalho

User = get_user_model()

class Command(BaseCommand):
    help = 'Popula o banco de dados com cabeleireiros e serviços fictícios'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população do banco...')

        # Lista de Profissionais e seus Serviços (Agora com 8)
        profissionais = [
            {
                'nome': 'Tony', 'sobrenome': 'Navalha', 'username': 'tony_barber',
                'servicos': [
                    {'nome': 'Barba Terapia', 'preco': 45.00, 'duracao': 40},
                    {'nome': 'Corte Degradê', 'preco': 50.00, 'duracao': 45},
                    {'nome': 'Acabamento', 'preco': 20.00, 'duracao': 15},
                ]
            },
            {
                'nome': 'Ana', 'sobrenome': 'Colorista', 'username': 'ana_color',
                'servicos': [
                    {'nome': 'Progressiva', 'preco': 120.00, 'duracao': 90},
                    {'nome': 'Platinado', 'preco': 180.00, 'duracao': 120},
                    {'nome': 'Hidratação', 'preco': 60.00, 'duracao': 40},
                ]
            },
            {
                'nome': 'Marcos', 'sobrenome': 'Style', 'username': 'marcos_style',
                'servicos': [
                    {'nome': 'Corte Social', 'preco': 60.00, 'duracao': 50},
                    {'nome': 'Degradê Navalhado', 'preco': 55.00, 'duracao': 50},
                    {'nome': 'Sobrancelha', 'preco': 15.00, 'duracao': 10},
                ]
            },
            {
                'nome': 'Julia', 'sobrenome': 'Visagista', 'username': 'julia_v',
                'servicos': [
                    {'nome': 'Consultoria + Corte', 'preco': 90.00, 'duracao': 60},
                    {'nome': 'Corte Infantil', 'preco': 45.00, 'duracao': 30},
                ]
            },
            {
                'nome': 'Ricardo', 'sobrenome': 'Santos', 'username': 'ricardo_old',
                'servicos': [
                    {'nome': 'Corte Máquina', 'preco': 35.00, 'duracao': 20},
                    {'nome': 'Barba Express', 'preco': 25.00, 'duracao': 15},
                ]
            },
            {
                'nome': 'Sofia', 'sobrenome': 'Penteados', 'username': 'sofia_braids',
                'servicos': [
                    {'nome': 'Tranças Box Braids', 'preco': 150.00, 'duracao': 120},
                    {'nome': 'Finalização', 'preco': 20.00, 'duracao': 15},
                ]
            },
            {
                'nome': 'Diego', 'sobrenome': 'Fade', 'username': 'diego_fade',
                'servicos': [
                    {'nome': 'Corte com Desenho (Freestyle)', 'preco': 60.00, 'duracao': 60},
                    {'nome': 'Pigmentação de Barba', 'preco': 35.00, 'duracao': 30},
                    {'nome': 'Luzes (Reflexo)', 'preco': 90.00, 'duracao': 90},
                ]
            },
            {
                'nome': 'Camila', 'sobrenome': 'Capilar', 'username': 'camila_hair',
                'servicos': [
                    {'nome': 'Selagem Térmica', 'preco': 150.00, 'duracao': 120},
                    {'nome': 'Cronograma Capilar', 'preco': 80.00, 'duracao': 60},
                    {'nome': 'Corte Bordado (Pontas Duplas)', 'preco': 70.00, 'duracao': 50},
                ]
            },
        ]

        for prof_data in profissionais:
            # 1. Criar Usuário (se não existir)
            user, created = User.objects.get_or_create(
                username=prof_data['username'],
                defaults={
                    'first_name': prof_data['nome'],
                    'last_name': prof_data['sobrenome'],
                    'email': f"{prof_data['username']}@salaovip.com",
                    'tipo': 'CABELEIREIRO',
                    'telefone': '(11) 99999-8888'
                }
            )
            
            if created:
                user.set_password('senha123') # Senha padrão para testes
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Profissional criado: {user.first_name}'))
            else:
                self.stdout.write(f'Profissional já existe: {user.first_name}')

            # 2. Configurar Horários (Resetar/Garantir)
            for dia in range(7):
                horario, _ = HorarioTrabalho.objects.get_or_create(
                    profissional=user,
                    dia_semana=dia
                )
                horario.hora_inicio = '09:00'
                horario.hora_fim = '18:00'
                horario.almoco_inicio = '12:00'
                horario.almoco_fim = '13:00'
                horario.folga = True if dia == 6 else False # Domingo é folga
                horario.save()

            # 3. Criar Serviços
            for serv_data in prof_data['servicos']:
                Servico.objects.get_or_create(
                    profissional=user,
                    nome=serv_data['nome'],
                    defaults={
                        'preco': serv_data['preco'],
                        'duracao_minutos': serv_data['duracao'],
                        'ativo': True
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('Banco de dados populado com 8 profissionais!'))