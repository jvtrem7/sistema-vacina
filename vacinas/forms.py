from django import forms
from .models import Paciente, Vacina

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nome', 'cpf', 'data_nascimento']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
class VacinaForm(forms.ModelForm):
    class Meta:
        model = Vacina
        fields = ['paciente', 'nome_vacina', 'lote']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'nome_vacina': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Pfizer, Coronavac...'}),
            'lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número do lote'}),
        }