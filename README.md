# School Circle

Base full stack inicial para o projeto **School Circle**, preparada para MVP com:

- Backend em Django + Django REST Framework
- Frontend em React + TypeScript + Vite
- PostgreSQL
- Docker Compose para desenvolvimento

## Estrutura

```text
.
├── backend/
├── frontend/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Tecnologias

### Backend

- Python
- Django
- Django REST Framework
- SimpleJWT
- django-cors-headers
- Pillow
- PostgreSQL

### Frontend

- React
- TypeScript
- Vite
- React Router
- Axios

## Como subir o projeto

1. Opcionalmente copie o arquivo de ambiente:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

1. Suba os containers:

```bash
docker compose up --build
```

1. Acesse:

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend: [http://localhost:8000](http://localhost:8000)
- Healthcheck da API: [http://localhost:8000/api/health/](http://localhost:8000/api/health/)

## Observações

- O backend sobe com migrações automáticas no start do container.
- O app `users` já usa `Custom User` desde o início para evitar problemas futuros com migrações.
- Os apps `groups`, `attendance`, `study` e `gamification` foram criados apenas como placeholders estruturais.
- Há comentários `TODO` nos pontos em que a implementação futura deve entrar.

## Próximos passos

- Criar os modelos de domínio reais por app
- Definir serializers e regras de negócio
- Implementar autenticação real com endpoints próprios
- Evoluir rotas protegidas no frontend
- Criar páginas reais do produto
