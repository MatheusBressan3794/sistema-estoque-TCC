from django.contrib import admin
from .models import Alimento, Lote, Movimentacao, Perfil, Etec

admin.site.register(Etec)
admin.site.register(Alimento)
admin.site.register(Lote)
admin.site.register(Movimentacao)
admin.site.register(Perfil)