# Usa uma imagem oficial do Python, versão estável e leve
FROM python:3.12-slim

# Define o diretório de trabalho dentro do contentor
WORKDIR /app

# Instala as dependências do sistema necessárias para o PostgreSQL
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o ficheiro de dependências e instala-as
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia todo o código do teu projeto para dentro do contentor
COPY . .

# Expõe a porta que o Django vai usar
EXPOSE 8000