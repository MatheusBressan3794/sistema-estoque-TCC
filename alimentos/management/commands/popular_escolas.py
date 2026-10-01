from django.core.management.base import BaseCommand
from alimentos.models import Etec

class Command(BaseCommand):
    help = 'Cadastra automaticamente ETECs, Fatecs e unidades AMS no sistema'

    def handle(self, *args, **options):
        escolas = [
            # Unidades em Araras
            {"codigo": "058", "nome": "Etec Prefeito Alberto Feres", "cidade": "Araras"},
            {"codigo": "245", "nome": "Fatec Araras - Dr. Tomislav Oreskovic", "cidade": "Araras"},
            {"codigo": "AMS01", "nome": "AMS - Administração e Desenvolvimento de Sistemas (Araras)", "cidade": "Araras"},
            
            # Outras unidades de referência no Estado de São Paulo
            {"codigo": "001", "nome": "Etec São Paulo", "cidade": "São Paulo"},
            {"codigo": "002", "nome": "Etec Getúlio Vargas", "cidade": "São Paulo"},
            {"codigo": "055", "nome": "Etec Bento Quirino", "cidade": "Campinas"},
            {"codigo": "204", "nome": "Fatec Campinas", "cidade": "Campinas"},
            {"codigo": "194", "nome": "Fatec São Paulo", "cidade": "São Paulo"},
        ]

        criadas = 0
        for item in escolas:
            # Atualiza o nome caso a escola já exista com outro texto
            escola, created = Etec.objects.update_or_create(
                codigo=item["codigo"],
                defaults={
                    "nome": item["nome"],
                    "cidade": item["cidade"]
                }
            )
            if created:
                criadas += 1
        
        self.stdout.write(self.style.SUCCESS(f"Sucesso! As unidades foram atualizadas no sistema."))