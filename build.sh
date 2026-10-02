#!/usr/bin/env bash
# Exit on error
set -o errexit

# Instala as dependências
pip install -r requirements.txt

# Executa as migrações da base de dados
python manage.py migrate

# Cadastra automaticamente as ETECs, Fatecs e AMS na produção
python manage.py popular_escolas

# Cria o superutilizador automaticamente sem precisar de shell paga
python manage.py createsuperuser --noinput || true

# Recolhe os ficheiros estáticos para o WhiteNoise funcionar
python manage.py collectstatic --no-input