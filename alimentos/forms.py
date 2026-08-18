from django import forms
from .models import Alimento

class AlimentoForm(forms.ModelForm):
    class Meta:
        model = Alimento
        fields = ['nome', 'quantidade', 'data_validade']
        widgets = {
            'data_validade': forms.DateInput(attrs={'type': 'date'})
        }