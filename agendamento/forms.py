from django import forms
from .models import Agendamento, Servico
from users.models import User

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['servico', 'profissional', 'data_hora_inicio']
        widgets = {
            'data_hora_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'servico': forms.Select(attrs={'class': 'form-control'}),
            'profissional': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas usuários que são CABELEIREIROS no campo de profissional
        self.fields['profissional'].queryset = User.objects.filter(tipo='CABELEIREIRO')