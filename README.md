# 🛡️ Stock Guardians

Sistema web de gestão e controlo de stock desenvolvido como Trabalho de Conclusão de Curso (TCC). A aplicação permite o registo, monitorização e rastreio de alimentos e lotes, garantindo maior eficiência e segurança no controlo de inventário.

---

## 🚀 Tecnologias Utilizadas

O projeto foi desenvolvido com tecnologias modernas de mercado:
* **Python 3.10+** & **Django 5.x** (Backend e ORM)
* **PostgreSQL 15** (Base de dados relacional principal)
* **Docker & Docker Compose** (Containerização do ambiente de base de dados)
* **Bootstrap / HTML5 / CSS3** (Interface de utilizador)
* **Python-Decouple** (Gestão segura de variáveis de ambiente)

---

## ⚙️ Pré-requisitos

Antes de iniciar, certifique-se de ter instalado na máquina:
* [Python](https://www.python.org/) (versão 3.10 ou superior)
* [Git](https://git-scm.com/)
* [Docker Desktop](https://www.docker.com/) a funcionar em segundo plano.

---

## 📦 Como Executar o Projeto noutra Máquina

Siga os passos abaixo para clonar e colocar o projeto a funcionar num novo computador:

### 1. Clonar o Repositório
Abra o terminal e clone o projeto para a sua máquina:
```bash
git clone <url-do-seu-repositorio-git>
cd sistema-estoque-TCC

### 2. Configurar o Ambiente Virtual (Python)
Crie e ative um ambiente virtual para isolar as dependências do projeto:

* **No Windows (CMD / PowerShell):**
  ```bash
  python -m venv venv
  venv\Scripts\activate

  ### 3. Instalar as Dependências
Com o ambiente virtual ativo, instale todas as bibliotecas necessárias:
```bash
pip install -r requirements.txt

### 4. Configurar as Variáveis de Ambiente (`.env`)
Na raiz do projeto (na mesma pasta onde está o `manage.py`), crie um ficheiro chamado **`.env`** e cole as seguintes configurações de acesso:
```env
DEBUG=True
SECRET_KEY=django-insecure-sua-chave-secreta-aqui
DB_NAME=stock_guardians_db
DB_USER=admin_estoque
DB_PASSWORD=senha_segura_123
DB_HOST=localhost
DB_PORT=5433

### Passo 5:
```markdown
### 5. Iniciar a Base de Dados via Docker
Suba o contentor do PostgreSQL configurado no Docker Compose:
```bash
docker-compose up -d

### Passo 6:
```markdown
### 6. Executar as Migrações do Django
Crie as tabelas estruturadas na base de dados PostgreSQL:
```bash
python manage.py migrate

### Passo 7 e Autores (Finalização):
```markdown
### 7. Iniciar o Servidor de Desenvolvimento
Por fim, execute o servidor local do Django:
```bash
python manage.py runserver

---

## 👨‍💻 Autores
* Rhuan Rafael Milares Alvarinho
* Matheus Bressan Vila Nova
* Yasmim Santos Vieira

**Projeto:** TCC - Stock Guardians