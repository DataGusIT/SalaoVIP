from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class ClienteRegistroForm(UserCreationForm):
    telefone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        # Definimos quais campos aparecem no cadastro
        fields = ['username', 'email', 'telefone'] 
        
        # Adicionamos classes CSS para ficar bonito com Bootstrap
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        # Forçamos que todo cadastro por aqui seja CLIENTE
        user = super().save(commit=False)
        user.tipo = 'CLIENTE'
        if commit:
            user.save()
        return user
    
class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telefone', 'foto']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), # Email apenas leitura por segurança
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }