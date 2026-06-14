\# SchoolCircle - Instruções para agentes



\## Ambiente



Este projeto roda com Docker Compose.



Não execute comandos Django diretamente no host Windows, pois o ambiente local pode não ter Django instalado.



Não use:



```bash

python manage.py makemigrations

python manage.py migrate

python manage.py test

python manage.py check

```



Use sempre comandos dentro do container `backend`:



```bash

docker compose exec backend python manage.py makemigrations

docker compose exec backend python manage.py migrate

docker compose exec backend python manage.py test

docker compose exec backend python manage.py check

```



Se os containers não estiverem rodando:



```bash

docker compose up -d

```



Para rodar um comando Django em container temporário:



```bash

docker compose run --rm backend python manage.py <comando>

```



\## Diretrizes gerais



\* Faça a menor alteração limpa possível.

\* Não reescreva o projeto inteiro.

\* Preserve funcionalidades existentes de login, registro, JWT e endpoints já usados pelo frontend.

\* Antes de alterar código, inspecione os arquivos relevantes: models, serializers, views, urls, settings, migrations e testes.

\* Use `get\_user\_model()` quando precisar referenciar o usuário.

\* Não use `django.contrib.auth.models.User` diretamente.

\* Não introduza dependências novas sem necessidade clara.



\## Django Admin



O SchoolCircle não terá painel administrativo/admin neste momento.



Portanto:



\* Não registrar models no Django Admin.

\* Não criar `ModelAdmin`.

\* Não criar `CustomUserAdmin`.

\* Não adicionar lógica dependente de `/admin/`.

\* Não usar Django Admin como justificativa para adicionar campos ao model.

\* Se um `admin.py` existir apenas para registrar model, deixe vazio ou remova o registro.

\* Não mexa em `/admin/` ou `django.contrib.admin` salvo se a issue pedir explicitamente ou se for necessário para não quebrar o projeto.



\## Model User



O model `User` deve respeitar ao máximo o diagrama conceitual:



\* `id`: UUID

\* `full\_name`: nome completo

\* `email`: único

\* `password`: hash da senha usando `set\_password()`

\* `date\_joined`: data de entrada/criação

\* `is\_active`: usuário ativo/inativo



Adaptação conceitual:



\* `fullName` no diagrama vira `full\_name` no Django.

\* `dateJoined` no diagrama vira `date\_joined` no Django.

\* `isActive` no diagrama vira `is\_active` no Django.

\* `passwordHash` no diagrama corresponde ao campo `password`, armazenado com hash.



Restrições para `User`:



\* Não usar `PermissionsMixin`, salvo se explicitamente solicitado.

\* Não adicionar `is\_staff`.

\* Não adicionar `is\_superuser`.

\* Não adicionar `groups`.

\* Não adicionar `user\_permissions`.

\* Não adicionar `username`.

\* Não adicionar `first\_name`.

\* Não adicionar `last\_name`.

\* Não criar `create\_superuser`, salvo se a issue pedir explicitamente.

\* Não expor senha em serializers ou respostas da API.



\## Autenticação e JWT



\* O login deve usar email e senha.

\* O login deve validar senha com `check\_password()`.

\* Usuário com `is\_active=False` não deve conseguir fazer login.

\* O login deve preservar o fluxo JWT existente.

\* Se usar SimpleJWT, preserve a compatibilidade com `access` e `refresh`.

\* Não reescreva a autenticação inteira para resolver uma mudança pequena.

\* Não implementar blacklist, rotação de refresh token ou logout server-side sem issue explícita.



\## Migrations e banco



\* Criar migrations quando alterar models.

\* Não apagar migrations antigas sem autorização explícita.

\* Não resetar o banco sem autorização explícita.

\* Não rodar `docker compose down -v` automaticamente.

\* Se houver inconsistência entre banco e migrations, relate o problema e sugira solução.

\* Em ambiente local/dev, reset destrutivo só pode ser sugerido, nunca executado sem confirmação.

\* Não criar migrations desnecessárias.



\## APIs



\* Endpoints sensíveis devem usar autenticação quando fizer sentido.

\* Preserve contratos já usados pelo frontend.

\* Não alterar nomes de campos de request/response sem necessidade.

\* Se alterar uma resposta da API, aponte o impacto no frontend.

\* IDs UUID devem ser tratados como string no frontend.



\## Frontend



\* Não mexa no frontend se a issue for apenas backend, salvo se houver quebra clara de contrato.

\* Se mexer no fluxo de auth, verificar uso de:



&#x20; \* `access\_token`

&#x20; \* `refresh\_token`

&#x20; \* logout

&#x20; \* interceptor Axios, se existir

\* Logout deve limpar todos os dados locais de sessão relevantes.



\## Testes e verificação



Sempre que possível, rode:



```bash

docker compose exec backend python manage.py check

docker compose exec backend python manage.py test

```



Se alterar migrations/modelos, também rode:



```bash

docker compose exec backend python manage.py makemigrations

docker compose exec backend python manage.py migrate

```



Se não conseguir rodar comandos por limitação do ambiente, informe claramente.



\## Ao finalizar



Sempre retorne:



1\. Resumo das mudanças feitas.

2\. Arquivos alterados.

3\. Como testar manualmente.

4\. Comandos executados ou recomendados.

5\. Pontos de atenção sobre banco/migrations.

6\. Qualquer impacto em login/JWT/frontend.

7\. Confirmação de que não foram adicionados campos/admin fora do escopo, quando a issue envolver `User`.



