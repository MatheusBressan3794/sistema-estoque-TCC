from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

# --- 1. TABELA DE ESCOLAS (ETEC) ---
class Etec(models.Model):
    codigo = models.CharField(max_length=10, unique=True, help_text="Ex: 058")
    nome = models.CharField(max_length=150, help_text="Ex: Etec Euro Albino de Souza")
    cidade = models.CharField(max_length=100, help_text="Ex: Araras")

    def __str__(self):
        return f"{self.nome} - {self.cidade}"


# --- 2. ALIMENTOS (Vinculados à ETEC) ---
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

    # Relação com a ETEC
    etec = models.ForeignKey(Etec, on_delete=models.CASCADE, related_name='alimentos', null=True, blank=True)

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
    

# --- 3. LOTES (Vinculados à ETEC) ---
class Lote(models.Model):
    etec = models.ForeignKey(Etec, on_delete=models.CASCADE, related_name='lotes', null=True, blank=True)

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


# --- 4. MOVIMENTAÇÕES ---
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
        return f"{this.tipo} - {self.lote.alimento.nome}"


# --- 5. PERFIL DO UTILIZADOR (Vinculado à ETEC) ---
class PerfilUsuario(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    
    etec = models.ForeignKey(Etec, on_delete=models.CASCADE, related_name='usuarios', null=True, blank=True)
    aprovado_diretora = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.etec})"