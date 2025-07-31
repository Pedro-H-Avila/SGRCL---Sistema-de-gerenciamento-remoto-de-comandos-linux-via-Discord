Sistema de Gerenciamento Remoto de Comandos Linux via Discord
Este projeto implementa um sistema didático para gerenciar remotamente comandos Linux em máquinas Ubuntu 22.04, usando um bot do Discord como interface, um serviço web com FastAPI e agentes Linux para execução de comandos. O sistema usa PostgreSQL para persistência de dados e SQLAlchemy como ORM.
Visão Geral
O sistema é composto por três componentes:

Bot do Discord (discord_bot.py): Interface para listar máquinas ativas, cadastrar scripts e agendar execuções.
Serviço Web (server.py): Intermediário que gerencia o banco PostgreSQL e comunicação com bot/agentes.
Agente Linux (agent.py): Roda em cada máquina Ubuntu, faz polling a cada 5 minutos e executa comandos.

Pré-requisitos

Python 3.8+ instalado em todos os ambientes.
Conta no Heroku para deploy do serviço web.
Banco PostgreSQL (ex.: Heroku Postgres ou local).
Bot do Discord configurado no Discord Developer Portal.
Máquinas Ubuntu 22.04 para os agentes.

Instalação
1. Clonar o Repositório
git clone <URL_DO_REPOSITORIO>
cd projeto

2. Instalar Dependências
pip install -r requirements.txt

3. Configurar Variáveis de Ambiente
Crie um arquivo .env na raiz do projeto com base em .env.example:
BOT_TOKEN=seu_token_do_bot_discord
API_URL=https://seu-app-heroku.herokuapp.com
DATABASE_URL=postgresql://user:pass@host:port/db
AUTHORIZED_USERS=123456789012345678,987654321098765432
MACHINE_NAME=maquina1
MACHINE_ID=uuid_gerado

4. Configurar o Bot do Discord

Crie um bot no Discord Developer Portal.
Copie o token e adicione ao .env (BOT_TOKEN).
Convide o bot para o seu servidor Discord com permissões de leitura/envio de mensagens.

5. Implantar o Serviço Web no Heroku

Crie um app no Heroku.
Adicione o add-on Heroku Postgres e copie a DATABASE_URL.
Configure a DATABASE_URL no Heroku (heroku config:set DATABASE_URL=...).
Deploy o código:heroku git:remote -a seu-app-heroku
git push heroku main


Verifique se o serviço está rodando: https://seu-app-heroku.herokuapp.com/docs.

6. Instalar o Agente Linux

Copie agent.py para /usr/local/bin/agent.py em uma máquina Ubuntu 22.04.
Crie um arquivo .env na mesma pasta com API_URL, MACHINE_NAME e MACHINE_ID.
Configure como serviço systemd:sudo nano /etc/systemd/system/linux-agent.service

Adicione:[Unit]
Description=Agente Linux para Gerenciamento Remoto
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/agent.py
WorkingDirectory=/usr/local/bin
Restart=always

[Install]
WantedBy=multi-user.target


Ative o serviço:sudo systemctl enable linux-agent
sudo systemctl start linux-agent



Instruções de Uso

Iniciar o Bot:python discord_bot.py


Comandos no Discord:
!list_machines: Lista máquinas ativas.
!register_script ls_dir "ls -l": Cadastra um script chamado ls_dir.
!execute_script maquina1 ls_dir: Agenda a execução do script ls_dir na máquina maquina1.


Verificar Resultados:
Consulte a tabela commands no banco PostgreSQL para ver o status e saída dos comandos.



Testes

Inicie o serviço web no Heroku.
Inicie o bot localmente ou em outra máquina.
Instale o agente em pelo menos uma máquina Ubuntu 22.04.
No Discord, use:
!list_machines para verificar se a máquina aparece.
!register_script test "echo Hello World" para cadastrar um script.
!execute_script maquina1 test para executar.


Verifique a tabela commands no banco para confirmar a saída (Hello World).

Notas de Segurança

HTTPS: Configure SSL no Heroku para proteger a comunicação.
Validação de Comandos: Antes de executar scripts, valide manualmente o conteúdo para evitar comandos perigosos (ex.: rm -rf /).
Permissões: Adicione apenas IDs confiáveis em AUTHORIZED_USERS.

Exemplo de Saída
Comando: !list_machinesResposta:
Máquinas ativas:
- maquina1 (ID: 550e8400-e29b-41d4-a716-446655440000)

Comando: !register_script ls_dir "ls -l"Resposta: Script 'ls_dir' cadastrado com sucesso!
Comando: !execute_script maquina1 ls_dirResposta: Comando agendado para 'maquina1' com o script 'ls_dir'!
Estrutura do Repositório
/projeto
├── discord_bot.py
├── server.py
├── agent.py
├── requirements.txt
├── .env.example
└── README.md

Licença
MIT License. Veja LICENSE para detalhes.