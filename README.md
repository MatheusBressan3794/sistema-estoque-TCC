# Stock Guardians

> Sistema web para gerenciamento de estoque de alimentos.

O **Stock Guardians** é uma aplicação desenvolvida para tornar o controle de alimentos mais simples, organizado e acessível. O sistema reúne o cadastro dos itens, o acompanhamento do estoque e a estrutura para registrar movimentações e consultar relatórios em uma interface moderna e responsiva.

A proposta é oferecer uma visão clara da despensa e ajudar no acompanhamento da quantidade e da validade dos alimentos, reduzindo esquecimentos e facilitando a rotina de gerenciamento.

## Funcionalidades

- Tela inicial de apresentação do sistema.
- Acesso e cadastro de usuários.
- Dashboard com visão geral do sistema.
- Cadastro de alimentos.
- Edição de alimentos cadastrados.
- Exclusão de alimentos com confirmação.
- Pesquisa de alimentos por nome.
- Visualização da quantidade disponível.
- Exibição da data de validade.
- Identificação visual do status do estoque.
- Área de movimentações.
- Área de relatórios.
- Layout responsivo para computador, tablet e celular.
- Interface personalizada com componentes reutilizáveis.

## Tecnologias utilizadas

### Back-end

- Python
- Django
- SQLite

### Front-end

- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Bootstrap Icons
- Django Templates

O projeto utiliza o sistema de templates do Django e mantém a separação entre a camada visual e a lógica da aplicação. Não utiliza React, Vue ou Angular.

## Organização do projeto

```text
sistema-estoque-TCC/
├── alimentos/
│   ├── migrations/
│   ├── static/alimentos/
│   │   ├── css/
│   │   └── js/
│   ├── templates/alimentos/
│   │   ├── partials/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── form.html
│   │   ├── inicio.html
│   │   └── lista.html
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── controle_estoque/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── manage.py
└── README.md
```

## Identidade visual

A interface foi criada com uma identidade visual inspirada em organização, praticidade e controle:

- **Laranja:** ações principais, destaques e atenção.
- **Verde:** disponibilidade, sucesso e informações positivas.
- **Branco:** áreas principais, cards e conteúdo.
- **Cinza claro:** divisões, fundos e elementos secundários.

O layout conta com sidebar responsiva, navegação superior, cards, badges, tabela moderna, formulários personalizados e estados vazios para melhorar a experiência de uso.

## Como executar o projeto

### Pré-requisitos

- Python 3.10 ou superior.
- Git.

### 1. Clone o repositório

```bash
git clone https://github.com/MatheusBressan3794/sistema-estoque-TCC.git
cd sistema-estoque-TCC
```

### 2. Crie um ambiente virtual

No Windows:

```bash
py -m venv venv
venv\Scripts\activate
```

No Linux ou macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale o Django

```bash
pip install django
```

### 4. Execute as migrações

```bash
python manage.py migrate
```

No Windows, também é possível utilizar:

```bash
py manage.py migrate
```

### 5. Inicie o servidor

```bash
python manage.py runserver
```

Acesse no navegador:

```text
http://127.0.0.1:8000/
```

## Rotas principais

| Página | Rota |
|---|---|
| Início | `/` |
| Login | `/login/` |
| Cadastro | `/cadastro/` |
| Dashboard | `/dashboard/` |
| Estoque | `/alimentos/` |
| Novo alimento | `/alimentos/criar/` |
| Movimentação | `/movimentacao/` |
| Relatórios | `/relatorios/` |

## Desenvolvedores

Este projeto foi desenvolvido por:

### Rhuan Alvarinho

Desenvolvedor do projeto e integrante responsável pela construção e evolução do sistema de gerenciamento de estoque.

### Matheus Bressan

Desenvolvedor do projeto e integrante responsável pela implementação, organização e publicação da aplicação.

### Yasmim Santos

Desenvolvedora do projeto e integrante responsável pela colaboração no desenvolvimento e na construção da experiência do sistema.

## Projeto acadêmico

O Stock Guardians foi desenvolvido como projeto de conclusão de curso, unindo desenvolvimento web, organização de dados e design de interfaces para solucionar uma necessidade prática de gerenciamento de estoque.

## Licença

Este projeto está disponível sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais informações.

---

Feito com dedicação por **Rhuan Alvarinho, Matheus Bressan e Yasmim Santos**.
