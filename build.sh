#!/usr/bin/env bash
# Exit on error
set -o errexit

# Instala as dependências
pip install -r requirements.txt

# Executa as migrações da base de dados
python manage.py migrate

# Recolhe os ficheiros estáticos para o WhiteNoise funcionar
python manage.py collectstatic --no-input