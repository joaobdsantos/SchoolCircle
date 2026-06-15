# School Circle

School Circle e uma PWA/mobile-first para estudantes registrarem presenca, sessoes de estudo, grupos, pontos e streaks.

## Stack

- Backend: Django, Django REST Framework, SimpleJWT, PostgreSQL
- Frontend: React, TypeScript, Vite, Axios
- Infra: Docker Compose

## Funcionalidades Implementadas

### Backend

- Cadastro e login com JWT
- Refresh token
- Atualizacao de conta
- Perfil academico
- Grupos de estudo
- Criacao automatica de membership `OWNER` ao criar grupo
- Memberships de grupo
- Convites de grupo no nivel de model e serializer
- Registro de presenca
- Registro de sessao de estudo
- Progresso global do usuario
- Historico de pontos
- Pontuacao automatica com Strategy + PointsService

### Frontend

- Login
- Cadastro
- Home
- Perfil academico
- Edicao de conta
- Refresh automatico do token

## Endpoints Principais

- `GET /api/health/`
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/token/refresh/`
- `PUT /api/auth/profile/`
- `GET /api/academic-profile/`
- `PUT /api/academic-profile/`
- `GET /api/groups/`
- `POST /api/groups/`
- `GET /api/groups/<uuid>/`
- `PUT /api/groups/<uuid>/`
- `GET /api/attendance-records/`
- `POST /api/attendance-records/`
- `GET /api/study-sessions/`
- `POST /api/study-sessions/`
- `GET /api/user-progress/`
- `GET /api/point-transactions/`

## Strategy de Pontuacao

O backend usa o padrao GoF Strategy para encapsular regras de pontuacao por tipo de atividade:

- `PointsStrategy`
- `AttendancePointsStrategy`
- `StudySessionPointsStrategy`
- `PointsService`

Fluxo atual:

`AttendanceRecord` ou `StudySession` -> `Strategy` -> `PointsService` -> `PointTransaction` -> `UserProgress`

Isso permite calcular pontos, motivo, origem e data da atividade sem espalhar regras de negocio pelos endpoints.

## O Que Ainda Falta Para o MVP

- Frontend de presenca
- Frontend de sessao de estudo
- Tela de progresso e historico de pontos
- Endpoints e fluxo completo de convites
- Aceitar convite criando membership
- Ranking de grupo
- Pontos de grupo
- Upload real de imagem

## Como Rodar

### Subir o projeto

```bash
docker compose up --build
```

### Rodar migracoes

```bash
docker compose exec backend python manage.py migrate
```

### Rodar testes do backend

```bash
docker compose exec backend python manage.py test
```

### Verificacao basica do Django

```bash
docker compose exec backend python manage.py check
```

### Acessos locais

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend: [http://localhost:8000](http://localhost:8000)
- Healthcheck da API: [http://localhost:8000/api/health/](http://localhost:8000/api/health/)

## Estrutura

```text
.
├── backend/
├── frontend/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Observacoes

- O backend sobe com migracoes automaticas no start do container.
- O projeto ja tem apps reais para `groups`, `attendance`, `study` e `gamification`.
- O painel administrativo do Django nao faz parte do escopo atual.
