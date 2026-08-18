from django.db import models

from django.db import models

class Alimento(models.Model):
    nome = models.CharField(max_length=100)
    quantidade = models.IntegerField()
    data_validade = models.DateField()

    def __str__(self):
        return f"{self.nome} - {self.quantidade} unidades"
