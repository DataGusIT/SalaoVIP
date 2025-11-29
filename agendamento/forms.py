from django import forms
from .models import Agendamento, Servico
from users.models import User

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['servico', 'profissional', 'data_hora_inicio']
        widgets = {
            'servico': forms.Select(attrs={'class': 'form-control'}),
            'profissional': forms.Select(attrs={'class': 'form-control', 'id': 'select-profissional'}),
            # ESCONDEMOS ESSE CAMPO. O Javascript vai preencher ele.
            'data_hora_inicio': forms.HiddenInput(), 
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profissional'].queryset = User.objects.filter(tipo='CABELEIREIRO')