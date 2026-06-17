# SchoolCircle

SchoolCircle e um MVP academico/mobile-first para estudantes registrarem presenca em aula, sessoes de estudo, participarem de grupos, acompanharem pontos, streaks e ranking. O backend expoe uma API REST em Django/DRF e o frontend consome essa API com React, TypeScript, Vite e Axios.

## Stack

- Backend: Django, Django REST Framework, SimpleJWT
- Banco de dados: PostgreSQL
- Frontend: React, TypeScript, Vite, Axios
- Infraestrutura local: Docker Compose

## Estado Atual Do MVP

O MVP ja possui os apps reais `users`, `groups`, `attendance`, `study` e `gamification`.

Funcionalidades implementadas:

- Cadastro, login por email/senha e refresh token com JWT.
- Atualizacao de conta do usuario autenticado.
- Perfil academico do usuario.
- Criacao e edicao de grupos de estudo.
- Criacao automatica de membership `OWNER` ao criar grupo.
- Listagem e detalhe de memberships ativos.
- Saida de membro comum do grupo.
- Convites de grupo com criacao, detalhe, aceite, recusa e cancelamento.
- Registro de presenca com periodo, foto e compartilhamento opcional em grupo.
- Registro de sessoes de estudo com descricao e foto.
- Gamificacao com progresso global, pontos totais, streak atual e maior streak.
- Historico de transacoes de pontos.
- Pontos de grupo via `group_points` quando uma presenca e compartilhada com grupo.
- Ranking de grupo com ordenacao por pontos.

Pendencias conhecidas:

- Upload/validacao de imagem ainda e simples para o escopo do MVP.
- Nao ha painel administrativo como parte do escopo atual.
- Nao ha logout server-side, blacklist ou rotacao de refresh token.
- Fluxos avancados de moderacao, transferencia de owner e recuperacao de senha nao fazem parte do MVP atual.

## Padroes GoF Aplicados

### Strategy Na Pontuacao

O backend usa Strategy para encapsular regras de pontuacao por tipo de atividade:

- `PointsStrategy`
- `AttendancePointsStrategy`
- `StudySessionPointsStrategy`
- `PointsService`

Fluxo geral:

```text
AttendanceRecord ou StudySession -> PointsStrategy -> PointsService -> PointTransaction -> UserProgress
```

### Command Nos Convites

O backend usa Command para executar acoes de convite de grupo:

- `GroupInviteCommand`
- `AcceptGroupInviteCommand`
- `DeclineGroupInviteCommand`
- `CancelGroupInviteCommand`

Esses comandos centralizam validacoes de ator, status pendente e efeitos como criar ou reativar membership ao aceitar convite.

## Endpoints Principais

Base local da API: `http://localhost:8000/api`

### Core

- `GET /api/health/`

### Autenticacao E Usuario

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/token/refresh/`
- `PUT /api/auth/profile/`

### Perfil Academico

- `GET /api/academic-profile/`
- `PUT /api/academic-profile/`

### Grupos, Memberships, Convites E Ranking

- `GET /api/groups/`
- `POST /api/groups/`
- `GET /api/groups/<group_id>/`
- `PUT /api/groups/<group_id>/`
- `GET /api/groups/<group_id>/members/`
- `GET /api/groups/<group_id>/members/<membership_id>/`
- `DELETE /api/groups/<group_id>/members/<membership_id>/leave/`
- `GET /api/groups/<group_id>/ranking/`
- `GET /api/groups/invites/`
- `POST /api/groups/invites/`
- `GET /api/groups/invites/<invite_id>/`
- `POST /api/groups/invites/<invite_id>/accept/`
- `POST /api/groups/invites/<invite_id>/decline/`
- `POST /api/groups/invites/<invite_id>/cancel/`

### Presenca

- `GET /api/attendance-records/`
- `POST /api/attendance-records/`

### Sessoes De Estudo

- `GET /api/study-sessions/`
- `POST /api/study-sessions/`

### Gamificacao

- `GET /api/user-progress/`
- `GET /api/point-transactions/`

## Como Rodar Com Docker Compose

Subir os containers:

```bash
docker compose up --build
```

Ou, se ja estiverem criados:

```bash
docker compose up -d
```

Aplicar migracoes:

```bash
docker compose exec backend python manage.py migrate
```

Acessos locais:

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend: [http://localhost:8000](http://localhost:8000)
- Healthcheck: [http://localhost:8000/api/health/](http://localhost:8000/api/health/)

Scripts reais do frontend:

```bash
docker compose exec frontend npm run dev
docker compose exec frontend npm run build
docker compose exec frontend npm run preview
```

## Dados De Demonstracao Local

Para popular um usuario de demonstracao com dados de progresso e streak, use:

```bash
docker compose exec backend python manage.py seed_demo_progress
```

Esse comando cria ou atualiza o usuario abaixo e recria dados demo para simular aproximadamente 20 dias consecutivos de progresso/streak:

- Email: `demo.grafico@schoolcircle.local`
- Senha: `SchoolCircle123!`

Use apenas em ambiente local ou demonstracao. Esses dados e credenciais nao devem ser usados em producao.

## Como Testar

Verificacao basica do Django:

```bash
docker compose exec backend python manage.py check
```

Testes automatizados do backend:

```bash
docker compose exec backend python manage.py test
```

Build do frontend:

```bash
docker compose exec frontend npm run build
```

## Cuidados De Desenvolvimento

- Execute comandos Django dentro do container `backend`; nao rode `python manage.py ...` diretamente no host Windows.
- Use `docker compose exec backend python manage.py <comando>` quando os containers estiverem rodando.
- Use `docker compose run --rm backend python manage.py <comando>` apenas quando precisar de um container temporario.
- Nao apague migrations antigas sem autorizacao explicita.
- Nao resete o banco e nao rode `docker compose down -v` sem confirmacao.
- Se alterar models, crie migrations e valide com `makemigrations`, `migrate`, `check` e `test` dentro do container.
- Preserve os contratos de auth/JWT usados pelo frontend, especialmente os campos `access` e `refresh`.
- O Django Admin nao faz parte do escopo atual do SchoolCircle.

## Estrutura

```text
.
├── backend/
├── frontend/
├── docker-compose.yml
├── AGENTS.md
├── .env.example
└── README.md
```
