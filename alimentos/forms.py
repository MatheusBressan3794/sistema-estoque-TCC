from django import forms
from .models import Alimento


class AlimentoForm(forms.ModelForm):

    class Meta:
        model = Alimento

        fields = [
            'nome',
            'unidade_medida',
            'peso',
            'quantidade_minima',
            'tipo_uso'
        ]