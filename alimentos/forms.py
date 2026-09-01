from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Alimento, Lote, Movimentacao

#Cadastro de alimentos
class AlimentoForm(forms.ModelForm):
    class Meta:
        model = Alimento
        fields = [
            'nome',
            'embalagem',
            'quantidade_embalagem',
            'unidade_medida',
            'quantidade_minima',
            'tipo_uso'
        ]
        widgets = {
            'quantidade_embalagem': forms.NumberInput(attrs={'min': '0', 'step': 'any', 'class': 'form-control'}),
            'quantidade_minima': forms.NumberInput(attrs={'min': '0', 'class': 'form-control'}),
        }

    # Validação para impedir valores menores que zero na quantidade da embalagem
    def clean_quantidade_embalagem(self):
        quantidade = self.cleaned_data.get('quantidade_embalagem')
        if quantidade is not None and quantidade < 0:
            raise forms.ValidationError("A quantidade da embalagem não pode ser negativa.")
        return quantidade

    # Validação para impedir valores menores que zero na quantidade mínima
    def clean_quantidade_minima(self):
        quantidade_minima = self.cleaned_data.get('quantidade_minima')
        if quantidade_minima is not None and quantidade_minima < 0:
            raise forms.ValidationError("A quantidade mínima não pode ser negativa.")
        return quantidade_minima

#Movimentação do estoque (lotes)
class MovimentacaoForm(forms.Form):

    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    ]

    tipo = forms.ChoiceField(
        label='Tipo de movimentação',
        choices=TIPO_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    alimento = forms.ModelChoiceField(
        label='Alimento',
        queryset=Alimento.objects.all(),
        empty_label='Selecione um alimento',
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    numero_lote = forms.CharField(
        label='Número do lote',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: ARZ2026-001'
            }
        )
    )

    quantidade = forms.IntegerField(
        label='Quantidade de embalagens',
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Quantidade'
            }
        )
    )

    data_validade = forms.DateField(
        label='Data de validade',
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )

#Criar conta
class CriarContaForm(UserCreationForm):
    first_name = forms.CharField(
        label="Nome completo",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Como podemos chamar você?'})
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Escolha um nome de usuário'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Crie uma senha segura'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirme sua senha'})