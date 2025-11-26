# Site de Barbearia

Este é um projeto de site para uma barbearia, desenvolvido com o objetivo de oferecer uma plataforma simples para apresentar serviços, horários de funcionamento e permitir agendamentos online. O site utiliza tecnologias como HTML, CSS, JavaScript, Django.

## Tecnologias Utilizadas

- **HTML**: Estruturação do conteúdo da página.
- **CSS**: Estilização e layout do site.
- **JavaScript**: Funcionalidades interativas, como agendamento de horário.
- **Django**: Framework backend para desenvolvimento da aplicação.
- **SQLite**: Banco de dados relacional para armazenar dados de agendamentos e usuários.

## Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas:

- Python 3.x
- Django 4.x

## Replicar Repositório


### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DA_PASTA>
```

### 2. Crie e ative um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```


### 4. Aplique as migrations

```bash

python3 manage.py makemigrations
python3 manage.py migrate
```

### 5. Execute o servidor de desenvolvimento

```bash

python3 manage.py runserver
```
