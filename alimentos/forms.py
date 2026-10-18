from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Alimento, Lote, Movimentacao, Etec, Perfil 

# Cadastro de alimentos (Usado para Edição)
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
        labels = {
            'quantidade_embalagem': 'Tamanho da embalagem (Peso/Volume)',
            'quantidade_minima': 'Estoque mínimo de alerta',
        }
        widgets = {
            'quantidade_embalagem': forms.NumberInput(attrs={'min': '0', 'step': 'any', 'class': 'form-control', 'placeholder': 'Ex: 5, 300...'}),
            'quantidade_minima': forms.NumberInput(attrs={'min': '0', 'class': 'form-control', 'placeholder': 'Ex: 10'}),
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


# Cadastro Inicial de Alimento (Exige o Lote junto)
class CriarAlimentoForm(AlimentoForm):
    numero_lote = forms.CharField(
        label='Número do lote',
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: LOTE-001'
            }
        )
    )
    data_validade = forms.DateField(
        label='Data de validade',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )
    quantidade_inicial = forms.IntegerField(
        label='Qtd. de embalagens neste lote',
        min_value=1,
        required=True,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Quantas unidades vieram?'
            }
        )
    )
    


# Editar lote
class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['alimento', 'numero_lote', 'quantidade_atual', 'data_validade']
        widgets = {
            'alimento': forms.Select(attrs={'class': 'form-control'}),
            'numero_lote': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # Validação para impedir quantidade negativa
    def clean_quantidade_atual(self):
        quantidade = self.cleaned_data.get('quantidade_atual')
        if quantidade is not None and quantidade < 0:
            raise forms.ValidationError("A quantidade não pode ser negativa.")
        return quantidade

# Select de lotes que guarda de qual alimento é cada lote (o JavaScript usa isso pra filtrar)
class LoteSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        instance = getattr(value, 'instance', None)
        if instance is not None:
            option['attrs']['data-alimento'] = instance.alimento_id
        return option

# Movimentação do estoque (lotes)
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

        # Lote que já existe (obrigatório na saída; na entrada pode ser trocado por um lote novo)
    numero_lote = forms.ModelChoiceField(
        label='Lote existente',
        queryset=Lote.objects.filter(quantidade_atual__gt=0).select_related('alimento'),
        empty_label='Selecione um lote',
        required=False,
        widget=LoteSelect(
            attrs={
                'class': 'form-control'
            }
        )
    )

    # Só na entrada: número de um lote novo, digitado pela pessoa
    novo_lote = forms.CharField(
        label='Ou digite um novo lote',
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: LOTE-003'
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
        required=False,  # Essencial para não obrigar na saída
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

        # Mostra só os alimentos e lotes da ETEC de quem está logado
    def __init__(self, *args, etec=None, **kwargs):
        super().__init__(*args, **kwargs)
        if etec is not None:
            self.fields['alimento'].queryset = Alimento.objects.filter(etec=etec)
            self.fields['numero_lote'].queryset = Lote.objects.filter(
                etec=etec, quantidade_atual__gt=0
            ).select_related('alimento')

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo')
        alimento = cleaned.get('alimento')
        lote = cleaned.get('numero_lote')
        novo_lote = (cleaned.get('novo_lote') or '').strip()
        data_validade = cleaned.get('data_validade')
        cleaned['novo_lote'] = novo_lote

        # Se tipo ou alimento estiverem inválidos, o erro deles já aparece sozinho
        if not tipo or not alimento:
            return cleaned

        if tipo == 'SAIDA':
            if not lote:
                self.add_error('numero_lote', 'Selecione o lote de onde as embalagens vão sair.')
                
            elif lote.alimento_id != alimento.id:
                self.add_error('numero_lote', 'Esse lote não pertence ao alimento selecionado.')

        elif tipo == 'ENTRADA':
            if lote and novo_lote:
                self.add_error('novo_lote', 'Escolha um lote existente OU digite um novo, não os dois.')

            elif not lote and not novo_lote:
                self.add_error('numero_lote', 'Selecione um lote existente ou digite um lote novo.')

            elif lote and lote.alimento_id != alimento.id:
                self.add_error('numero_lote', 'Esse lote não pertence ao alimento selecionado.')

            elif novo_lote:
                ja_existe = Lote.objects.filter(
                    alimento=alimento, numero_lote=novo_lote
                ).exists()
                
                if not ja_existe and not data_validade:
                    self.add_error('data_validade', 'Informe a data de validade para criar um lote novo.')

        return cleaned


# Criar conta com associação correta da ETEC e Perfil
class CriarContaForm(UserCreationForm):
    
    etec = forms.ModelChoiceField(
        queryset=Etec.objects.all(),
        required=True,
        label="Selecione a sua ETEC",
        empty_label="Escolha uma escola...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

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

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado no sistema. Por favor, utilize outro ou faça login.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        
        if commit:
            user.save()
            Perfil.objects.update_or_create(
                user=user,
                defaults={
                    'etec': self.cleaned_data['etec'],
                    'email_verificado': False
                }
            )
        return user