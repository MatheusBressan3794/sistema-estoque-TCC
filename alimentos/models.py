from django.db import models
from django.core.validators import MinValueValidator  # Importação necessária para a validação

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
        validators=[MinValueValidator(0.0)]  # Impede valores negativos
    )

    unidade_medida = models.CharField(
        max_length=5,
        choices=UNIDADES_MEDIDA
    )

    quantidade_minima = models.IntegerField(
        validators=[MinValueValidator(0)]  # Impede valores negativos
    )

    tipo_uso = models.CharField(
        max_length=10,
        choices=TIPOS_USO
    )

    def __str__(self):
        return self.nome
    

class Lote(models.Model):

    alimento = models.ForeignKey(
        Alimento,
        on_delete=models.CASCADE,
        related_name='lotes'
    )

    numero_lote = models.CharField(max_length=100)

    quantidade_atual = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]  # Estoque não pode ficar negativo
    )

    data_validade = models.DateField()

    def __str__(self):
        return f"{self.alimento.nome} - Lote {self.numero_lote}"


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
        validators=[MinValueValidator(1)]  # Movimentação tem que ser pelo menos 1
    )

    data_movimentacao = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.tipo} - {self.lote.alimento.nome}"