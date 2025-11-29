from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Cria um superusuário automaticamente se não existir (via variáveis de ambiente)'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Pega os dados das variáveis de ambiente (com valores padrão caso esqueça)
        username = os.environ.get('SUPER_USER_NAME', 'admin')
        email = os.environ.get('SUPER_USER_EMAIL', 'admin@admin.com')
        password = os.environ.get('SUPER_USER_PASSWORD', 'admin123')

        # Verifica se o usuário já existe
        if not User.objects.filter(username=username).exists():
            self.stdout.write(f'Criando superusuário "{username}"...')
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superusuário "{username}" criado com sucesso!'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superusuário "{username}" já existe. Nenhuma ação necessária.'))