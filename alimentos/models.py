from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

# --- 1. ALIMENTOS ---
class Alimento(models.Model):

    EMBALAGENS = [
        ('PACOTE', 'Pacote'),
        ('CAIXA', 'Caixa'),
        ('LATA', 'Lata'),
        ('VIDRO', 'Vidro'),
        ('GARRAFA', 'Garrafa'),
        ('POTE', 'Pote'),
        ('SACO', 'Saco'),
    ]

    UNIDADES_MEDIDA = [
        ('KG', 'kg'),
        ('G', 'g'),
        ('L', 'L'),
        ('ML', 'ml'),
    ]

    TIPOS_USO = [
        ('LANCHE', 'Lanche'),
        ('ALMOCO', 'Almoço'),
    ]

    nome = models.CharField(max_length=100)

    embalagem = models.CharField(
        max_length=20,
        choices=EMBALAGENS
    )

    quantidade_embalagem = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )

    unidade_medida = models.CharField(
        max_length=5,
        choices=UNIDADES_MEDIDA
    )

    quantidade_minima = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    tipo_uso = models.CharField(
        max_length=10,
        choices=TIPOS_USO
    )

    def __str__(self):
        return self.nome
        
    @property
    def quantidade_total(self):
        total = sum(lote.quantidade_atual for lote in self.lotes.all())
        return total if total else 0
    

# --- 2. LOTES ---
class Lote(models.Model):
    alimento = models.ForeignKey(
        Alimento,
        on_delete=models.CASCADE,
        related_name='lotes'
    )

    numero_lote = models.CharField(max_length=100)

    quantidade_atual = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    data_validade = models.DateField()

    def __str__(self):
        return f"{self.alimento.nome} - Lote {self.numero_lote}"


# --- 3. MOVIMENTAÇÕES ---
class Movimentacao(models.Model):

    TIPOS = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    ]

    lote = models.ForeignKey(
        Lote,
        on_delete=models.PROTECT,
        related_name='movimentacoes'
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPOS
    )

    quantidade = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    data_movimentacao = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.tipo} - {self.lote.alimento.nome}"


# --- 4. PERFIL DO UTILIZADOR ---
class Perfil(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    email_verificado = models.BooleanField(default=False)
    aprovado_diretora = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username