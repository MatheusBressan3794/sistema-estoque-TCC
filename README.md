## 1. Clonar o Repositório

Abra o terminal e clone o projeto para sua máquina:

```bash
git clone <url-do-seu-repositorio-git>
cd sistema-estoque-TCC
```

## 2. Configurar o Ambiente Virtual (Python)

Crie e ative um ambiente virtual para isolar as dependências do projeto:

* **No Windows (CMD / PowerShell):**

```bash
python -m venv venv
venv\Scripts\activate
```

## 3. Instalar as Dependências

Com o ambiente virtual ativo, instale todas as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

## 4. Configurar as Variáveis de Ambiente (`.env`)

Na raiz do projeto (na mesma pasta onde está o `manage.py`), crie um ficheiro chamado `.env` e cole o seguinte conteúdo:

```env
DEBUG=True
SECRET_KEY=django-insecure-sua-chave-secreta-aqui
DB_NAME=stock_guardians_db
DB_USER=admin_estoque
DB_PASSWORD=senha_segura_123
DB_HOST=localhost
DB_PORT=5433
```

## 5. Iniciar a Base de Dados via Docker

Suba o contentor do PostgreSQL configurado no Docker Compose:

```bash
docker-compose up -d
```

## 6. Executar as Migrações do Django

Crie as tabelas estruturadas na base de dados PostgreSQL:

```bash
python manage.py migrate
```

## 7. Iniciar o Servidor de Desenvolvimento

Por fim, execute o servidor local do Django:

```bash
python manage.py runserver
```

---

## 👨‍💻 Autores
* Rhuan Rafael Milares Alvarinho
* Matheus Bressan Vila Nova
* Yasmim Santos Vieira

**Projeto:** TCC - Stock Guardians