from django.db import models

from django.db import models

from django.db import models


class Alimento(models.Model):

    TIPOS_USO = [
        ('LANCHE', 'Lanche'),
        ('ALMOCO', 'Almoço'),
    ]

    nome = models.CharField(max_length=100)

    unidade_medida = models.CharField(max_length=50)

    peso = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantidade_minima = models.IntegerField()

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

    data_validade = models.DateField()

    quantidade_atual = models.IntegerField(default=0)

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

    quantidade = models.IntegerField()

    data_movimentacao = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.tipo} - {self.lote.alimento.nome}"