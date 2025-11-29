from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ClienteRegistroForm, PerfilForm
from agendamento.models import Portfolio
from .models import User

def home(request):
    # prefetch_related('servicos', 'portfolio') faz uma mágica de performance:
    # carrega tudo em apenas 2 ou 3 consultas ao banco, em vez de 1 consulta por cabeleireiro.
    profissionais = User.objects.filter(tipo='CABELEIREIRO').prefetch_related('servicos', 'portfolio')
    
    return render(request, 'home.html', {'profissionais': profissionais})

def registro(request):
    if request.method == 'POST':
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso! Faça login.')
            return redirect('login')
    else:
        form = ClienteRegistroForm()
    return render(request, 'users/registro.html', {'form': form})

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        # instance=request.user carrega os dados atuais do usuário no formulário
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('editar_perfil')
    else:
        form = PerfilForm(instance=request.user)
    
    return render(request, 'users/perfil.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        # CORREÇÃO: Pegamos o usuário do formulário, não da request
        usuario = form.get_user()
        
        # Define o nome para exibir (Primeiro nome ou Username)
        nome = usuario.first_name if usuario.first_name else usuario.username
        
        messages.success(self.request, f"Bem-vindo(a) de volta, {nome}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Usuário ou senha incorretos. Tente novamente.")
        return super().form_invalid(form)

# 2. VIEW DE LOGOUT CUSTOMIZADA
def custom_logout(request):
    logout(request)
    messages.info(request, "Você saiu do sistema. Até logo!") # Toast de despedida
    return redirect('home')

def lista_profissionais(request):
    # Pega apenas usuários do tipo cabeleireiro
    profissionais = User.objects.filter(tipo='CABELEIREIRO')
    return render(request, 'users/profissionais.html', {'profissionais': profissionais})

