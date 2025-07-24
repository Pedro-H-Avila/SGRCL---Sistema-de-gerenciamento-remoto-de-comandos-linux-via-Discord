### Especificação do Projeto: Sistema de Gerenciamento Remoto de Comandos Linux via Discord com PostgreSQL

#### Objetivo
Desenvolver um sistema didático e simples para gerenciamento remoto de comandos Linux em um parque de 10 máquinas Ubuntu 22.04, utilizando um bot do Discord como interface de comando, um serviço web como intermediário e agentes instalados nas máquinas Linux para execução dos comandos. O sistema deve ser implementado com PostgreSQL como banco de dados (devido à necessidade de persistência em ambientes como Heroku, que apaga arquivos locais como os do SQLite) e um ORM para facilitar o acesso aos dados. A solução deve ser publicada em um repositório público no GitHub, com documentação clara e prática para instalação e execução, voltada para estagiários com conhecimento básico.

---

### Escopo do Sistema

O sistema é composto por três componentes principais:

1. **Bot do Discord**:
   - Interface principal para interação com usuários autorizados.
   - Permite listar máquinas ativas, cadastrar scripts e agendar a execução de scripts em máquinas específicas.
   - Implementado em Python usando a biblioteca `discord.py`.

2. **Serviço Web**:
   - Intermediário entre o bot do Discord e os agentes Linux.
   - Gerencia um banco de dados PostgreSQL para registrar máquinas ativas, scripts e comandos.
   - Implementado em Python usando FastAPI para simplicidade e deploy fácil (ex.: Heroku).
   - Usa um ORM (SQLAlchemy) para acesso ao banco de dados.

3. **Agente Linux**:
   - Instalado em cada máquina Ubuntu 22.04, rodando como serviço `systemd`.
   - Consulta o serviço web a cada 5 minutos (ping) para se registrar como ativa e verificar comandos pendentes.
   - Executa comandos e retorna resultados ao servidor.
   - Implementado em Python, com comunicação segura via polling.

---

### Requisitos Funcionais

#### 1. Bot do Discord
- **Comandos Disponíveis**:
  - `!list_machines`: Lista todas as máquinas ativas (que enviaram um "ping" ao servidor nos últimos 5 minutos).
  - `!register_script <nome> <conteúdo>`: Cadastra um script no servidor com um nome único e seu conteúdo (ex.: comandos Linux como `ls -l`).
  - `!execute_script <nome_máquina> <nome_script>`: Agenda a execução de um script cadastrado em uma máquina específica.
- **Permissões**:
  - Apenas usuários autorizados (definidos por uma lista de IDs do Discord no código ou em arquivo de configuração) podem executar comandos.
  - Usuários não autorizados recebem uma mensagem de erro no Discord.
- **Interação com o Serviço Web**:
  - Usa requisições HTTP (GET/POST) para comunicar-se com o serviço web.
  - Exibe respostas do servidor (ex.: lista de máquinas, confirmação de cadastro, erros) no canal do Discord.

#### 2. Serviço Web
- **Funcionalidades**:
  - Gerencia um banco de dados PostgreSQL com:
    - **Máquinas**: Registro de máquinas ativas (ID único, nome, última atividade).
    - **Scripts**: Scripts cadastrados (nome, conteúdo).
    - **Comandos**: Comandos pendentes e completados (máquina, script, status, saída).
  - Endpoints RESTful:
    - `GET /machines`: Retorna máquinas ativas (que pingaram nos últimos 5 minutos).
    - `POST /register_machine`: Registra ou atualiza uma máquina (enviado pelo agente).
    - `POST /scripts`: Cadastra um script (enviado pelo bot).
    - `POST /execute`: Agenda um comando para uma máquina (enviado pelo bot).
    - `GET /commands/{machine_id}`: Retorna comandos pendentes para um agente.
    - `POST /commands/{command_id}/result`: Recebe a saída de um comando executado.
- **Banco de Dados**:
  - Usar **PostgreSQL** para persistência, já que arquivos locais (como SQLite) são apagados em plataformas como Heroku.
  - Usar **SQLAlchemy** como ORM para facilitar operações no banco.
  - Estrutura do banco:
    - Tabela `machines`: `id` (texto, chave primária), `name` (texto), `last_seen` (inteiro, timestamp Unix).
    - Tabela `scripts`: `name` (texto, chave primária), `content` (texto).
    - Tabela `commands`: `id` (inteiro, autoincremento), `machine_id` (texto, chave estrangeira), `script_name` (texto), `status` (texto, ex.: "pending" ou "completed"), `output` (texto, saída do comando).
- **Comunicação**:
  - Recebe requisições HTTP do bot e dos agentes.
  - Responde com JSON contendo dados ou mensagens de status.

#### 3. Agente Linux
- **Funcionalidades**:
  - Registra-se no serviço web com um ID único (ex.: UUID gerado na instalação) e um nome configurável (ex.: `maquina1`).
  - Envia um "ping" ao serviço web a cada 5 minutos para se marcar como ativa.
  - Consulta o serviço web no mesmo intervalo para verificar comandos pendentes.
  - Executa comandos recebidos usando `subprocess`, capturando stdout e stderr.
  - Envia a saída do comando ao serviço web para armazenamento no banco.
- **Execução Contínua**:
  - Rodar como serviço `systemd` em cada máquina Ubuntu 22.04.
  - Configurado para reiniciar automaticamente em caso de falha.
- **Segurança**:
  - Usa polling (consultas periódicas) para evitar abrir portas de entrada.
  - Comunicação via HTTP (HTTPS em produção).

---

### Requisitos Não Funcionais

1. **Didático e Simples**:
   - O código deve ser claro, com comentários explicativos para estagiários com conhecimento básico.
   - Usar FastAPI e SQLAlchemy para minimizar a complexidade de implementação.
   - Evitar configurações complexas no deploy (ex.: Heroku para o serviço web).

2. **Segurança**:
   - Em produção, o serviço web deve usar HTTPS (ex.: configurar SSL no Heroku ou com Let's Encrypt).
   - Validar comandos para evitar execução de scripts perigosos (ex.: verificar conteúdo antes de executar).
   - Restringir acesso ao bot via lista de IDs de usuários.

3. **Persistência**:
   - Usar PostgreSQL para garantir que os dados não sejam apagados em plataformas como Heroku.
   - Configurar o banco com URL de conexão (ex.: `postgresql://user:pass@host/db`).

4. **Deploy**:
   - O serviço web deve ser implantável no Heroku (ou similar) com configuração mínima.
   - O bot pode rodar em qualquer máquina com acesso à internet (ex.: servidor local ou na nuvem).
   - O agente Linux deve ser fácil de instalar em qualquer Ubuntu 22.04.

5. **Manutenibilidade**:
   - Código modular, com funções separadas para cada funcionalidade.
   - Logs simples (ex.: print ou arquivo de log) para auditoria de erros.

---

### Decisões de Implementação

1. **Linguagem e Ferramentas**:
   - **Python 3.8+** para todos os componentes, pela familiaridade e bibliotecas disponíveis.
   - **discord.py** para o bot do Discord.
   - **FastAPI** para o serviço web, por ser simples e compatível com Heroku.
   - **SQLAlchemy** como ORM para interagir com o PostgreSQL.
   - **aiohttp** para requisições HTTP assíncronas no bot e agente.

2. **Banco de Dados**:
   - **PostgreSQL** para persistência, com conexão configurada via variável de ambiente (ex.: `DATABASE_URL`).
   - Tabelas criadas automaticamente na inicialização do serviço web.
   - Máquinas são consideradas ativas se pingarem o servidor nos últimos 5 minutos.

3. **Comunicação**:
   - Agentes usam polling a cada 5 minutos para registrar atividade e verificar comandos.
   - Comunicação via HTTP (HTTPS em produção) para segurança.
   - Endpoints protegidos por validação simples (ex.: checar ID da máquina).

4. **Agente Linux**:
   - Script Python único, instalado em `/usr/local/bin/agent.py`.
   - Configurado como serviço `systemd` com reinicialização automática.
   - Nome da máquina e ID único configuráveis no script ou em arquivo de configuração.

5. **Permissões**:
   - Lista estática de IDs de usuários autorizados no bot (no código ou arquivo `.env`).
   - O serviço web valida a existência de máquinas e scripts antes de processar comandos.

---

### Limitações

1. **Segurança**:
   - Sem HTTPS, a comunicação pode ser interceptada. Em produção, configurar SSL é obrigatório.
   - Comandos shell podem ser perigosos se não validados (ex.: evitar `rm -rf /`).
   - Permissões baseadas em lista estática podem ser difíceis de gerenciar para muitos usuários.

2. **Escalabilidade**:
   - Polling a cada 5 minutos pode gerar carga no servidor com muitas máquinas.
   - PostgreSQL é escalável, mas o Heroku tem limites no plano gratuito.

3. **Funcionalidade**:
   - Resultados de comandos são salvos no banco, mas não notificados automaticamente no Discord.
   - Não há suporte inicial para execução paralela de comandos na mesma máquina.

---

### Entregáveis

O estagiário deve entregar o projeto em um **repositório público no GitHub**, contendo:

1. **Código-Fonte**:
   - `discord_bot.py`: Bot do Discord com os comandos especificados.
   - `server.py`: Serviço web com FastAPI e SQLAlchemy para PostgreSQL.
   - `agent.py`: Agente Linux para instalação nas máquinas Ubuntu.
   - `requirements.txt`: Lista de dependências (ex.: `discord.py`, `fastapi`, `sqlalchemy`, `aiohttp`, `psycopg2-binary`).

2. **Documentação** (no arquivo `README.md`):
   - **Visão Geral**: Explicação do sistema e sua arquitetura (bot, serviço web, agente).
   - **Pré-requisitos**:
     - Python 3.8+.
     - Conta no Heroku para o serviço web.
     - Banco PostgreSQL (ex.: Heroku Postgres ou local).
     - Bot do Discord configurado no Developer Portal.
   - **Instruções de Instalação**:
     - Como configurar o bot (criar no Discord Developer Portal, obter token, convidar ao servidor).
     - Como implantar o serviço web no Heroku (incluindo configuração de `DATABASE_URL`).
     - Como instalar o agente em uma máquina Ubuntu (copiar script, configurar `systemd`, definir nome/ID).
   - **Instruções de Uso**:
     - Exemplos de comandos (`!list_machines`, `!register_script ls_dir "ls -l"`, `!execute_script maquina1 ls_dir`).
     - Como verificar resultados no banco (ex.: consultar tabela `commands`).
   - **Testes**:
     - Passos para testar o sistema (ex.: cadastrar script, executar em uma máquina, verificar saída no banco).
     - Incluir capturas de tela do Discord ou logs no `README.md`.
   - **Notas de Segurança**:
     - Recomendações para HTTPS e validação de comandos.
     - Como configurar variáveis de ambiente (ex.: `BOT_TOKEN`, `DATABASE_URL`).

3. **Estrutura do Repositório**:
   ```
   /projeto
   ├── discord_bot.py
   ├── server.py
   ├── agent.py
   ├── requirements.txt
   ├── .env.example
   └── README.md
   ```

4. **Testes**:
   - Testar em pelo menos uma máquina Ubuntu 22.04.
   - Implantar o serviço web no Heroku com PostgreSQL.
   - Demonstrar no `README.md` que os comandos funcionam (ex.: logs ou capturas de tela).

---

### Tarefas para o Estagiário

1. **Configurar o Ambiente**:
   - Instalar Python 3.8+ e dependências (`discord.py`, `fastapi`, `sqlalchemy`, `aiohttp`, `psycopg2-binary`).
   - Criar um bot no Discord Developer Portal e obter o token.
   - Configurar um banco PostgreSQL (ex.: Heroku Postgres ou local).

2. **Implementar o Bot do Discord**:
   - Criar os comandos `!list_machines`, `!register_script`, `!execute_script`.
   - Configurar permissões com base em IDs de usuários.
   - Testar integração com o serviço web via HTTP.

3. **Implementar o Serviço Web**:
   - Configurar FastAPI com endpoints RESTful.
   - Usar SQLAlchemy para gerenciar o banco PostgreSQL.
   - Testar endpoints com `curl` ou Postman.

4. **Implementar o Agente Linux**:
   - Criar script Python para polling (5 minutos) e execução de comandos.
   - Configurar como serviço `systemd` no Ubuntu 22.04.
   - Testar comunicação com o serviço web e execução de comandos.

5. **Documentar e Publicar**:
   - Escrever um `README.md` claro com instruções detalhadas.
   - Publicar o projeto em um repositório público no GitHub.
   - Incluir exemplos e capturas de tela.

---

### Prazo e Suporte

- **Prazo Sugerido**: 2-3 semanas para desenvolvimento, testes e documentação.
- **Suporte**: Consultar documentações de `discord.py`, `fastapi`, `sqlalchemy` e `systemd`. Para dúvidas, contatar o supervisor.

Essa especificação é clara, didática e otimizada para estagiários, com foco em PostgreSQL, deploy no Heroku e uso de SQLAlchemy para facilitar o aprendizado. Se precisar de ajustes ou mais detalhes, é só pedir!
