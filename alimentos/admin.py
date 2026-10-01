from django.contrib import admin
from .models import Alimento, Lote, Movimentacao, PerfilUsuario, Etec # Adicione o Etec aqui

admin.site.register(Etec)
# ... (os restantes registos que já tem)