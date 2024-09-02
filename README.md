readme_content = """
# Sistema de Gerenciamento de Assinaturas Digitais - Backend

Este repositório contém o código-fonte do backend para o sistema de gerenciamento de assinaturas digitais, desenvolvido utilizando o Django Rest Framework (DRF). O sistema foi projetado para fornecer uma API segura e eficiente para capturar, armazenar e gerenciar assinaturas digitais.

## **Pré-requisitos**

Antes de iniciar, certifique-se de ter os seguintes requisitos instalados:

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)
- Virtualenv (opcional, mas recomendado)
- Git

## **Instalação**

Siga os passos abaixo para configurar e iniciar o backend do projeto:

### 1. Clone o repositório

```bash
git clone https://github.com/MoisesMonter/signature_back.git
cd signature_back
```

### 2. Crie um ambiente virtual (opcional, mas recomendado)

```bash
python -m venv venv
```

Ative o ambiente virtual:

- **Windows:**
  ```bash
  venv\\Scripts\\activate
  ```

- **MacOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis de ambiente:

```env
DJANGO_SECRET_KEY='sua-chave-secreta-aqui'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

Certifique-se de substituir `'sua-chave-secreta-aqui'` por uma chave segura. Você pode usar o comando abaixo para gerar uma chave segura:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 5. Migre o banco de dados

```bash
python manage.py migrate
```

### 6. Crie um superusuário (opcional, para acessar o painel administrativo)

```bash
python manage.py createsuperuser
```

### 7. Execute o servidor de desenvolvimento

```bash
python manage.py runserver
```

O backend estará disponível em `http://127.0.0.1:8000/`.

## **Testes**

Para executar os testes automatizados, utilize o comando:

```bash
python manage.py test
```

## **Contribuição**

Se deseja contribuir para o projeto, siga os seguintes passos:

1. Faça um fork do projeto.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`).
3. Realize as modificações desejadas.
4. Faça um commit das suas mudanças (`git commit -am 'Adicione nova feature'`).
5. Faça um push para a branch (`git push origin feature/nova-feature`).
6. Abra um Pull Request.

## **Licença**

Este projeto é licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
"""
