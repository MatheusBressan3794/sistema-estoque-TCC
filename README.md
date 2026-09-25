## 1. Clonar o Repositório

Abra o terminal e clone o projeto para sua máquina:

```bash
git clone <url-do-seu-repositorio-git>
cd sistema-estoque-TCC
```

## 2. Configurar o Ambiente Virtual (Python)

Crie e ative um ambiente virtual para isolar as dependências do projeto antes de instalar os pacotes:

* **No Windows (CMD / PowerShell):**

```bash
py -m venv venv
venv\Scripts\activate
```

## 3. Instalar as Dependências

Com o ambiente virtual criado e ativo, instale todas as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

### 4. Configurar as Variáveis de Ambiente ( .env )

Na raiz do projeto (na mesma pasta onde está o `manage.py`), crie um ficheiro chamado `.env` e cole o seguinte conteúdo com as suas credenciais reais:

```env
DEBUG=True
SECRET_KEY=django-insecure-sua-chave-secreta-aqui
DATABASE_URL=cole_aqui_a_sua_string_de_conexao_do_supabase
BREVO_API_KEY=cole_aqui_a_sua_chave_de_api_do_brevo
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

## 👨‍💻 Autores

* Rhuan Rafael Milares Alvarinho
* Matheus Bressan Vila Nova
* Yasmim Santos Vieira

**Projeto:** TCC - Stock Guardians