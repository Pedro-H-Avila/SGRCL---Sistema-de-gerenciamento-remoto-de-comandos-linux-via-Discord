# discord_bot.py
# Bot do Discord para gerenciar comandos de máquinas Linux remotamente.
# Usa discord.py para interagir com o Discord e aiohttp para se comunicar com o serviço web.

import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")
AUTHORIZED_USERS = [int(id) for id in os.getenv("AUTHORIZED_USERS", "").split(",")]

# Configura o bot com prefixo '!' e intents para mensagens
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Evento: Bot iniciado
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# Função auxiliar para verificar se o usuário é autorizado
def is_authorized(ctx):
    return ctx.author.id in AUTHORIZED_USERS

# Comando: !list_machines
# Lista máquinas ativas (que pingaram nos últimos 5 minutos)
@bot.command()
async def list_machines(ctx):
    if not is_authorized(ctx):
        await ctx.send("Você não tem permissão para usar este comando.")
        return
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/machines") as resp:
            if resp.status == 200:
                machines = await resp.json()
                if machines:
                    response = "Máquinas ativas:\n" + "\n".join([f"- {m['name']} (ID: {m['id']})" for m in machines])
                else:
                    response = "Nenhuma máquina ativa no momento."
                await ctx.send(response)
            else:
                await ctx.send("Erro ao listar máquinas. Tente novamente.")

# Comando: !register_script <nome> <conteúdo>
# Cadastra um script no servidor
@bot.command()
async def register_script(ctx, name: str, *, content: str):
    if not is_authorized(ctx):
        await ctx.send("Você não tem permissão para usar este comando.")
        return
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/scripts", json={"name": name, "content": content}) as resp:
            if resp.status == 201:
                await ctx.send(f"Script '{name}' cadastrado com sucesso!")
            else:
                error = await resp.json()
                await ctx.send(f"Erro ao cadastrar script: {error.get('detail', 'Erro desconhecido')}")

# Comando: !execute_script <nome_máquina> <nome_script>
# Agenda a execução de um script em uma máquina
@bot.command()
async def execute_script(ctx, machine_name: str, script_name: str):
    if not is_authorized(ctx):
        await ctx.send("Você não tem permissão para usar este comando.")
        return
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/execute", json={"machine_name": machine_name, "script_name": script_name}) as resp:
            if resp.status == 201:
                await ctx.send(f"Comando agendado para '{machine_name}' com o script '{script_name}'!")
            else:
                error = await resp.json()
                await ctx.send(f"Erro ao agendar comando: {error.get('detail', 'Erro desconhecido')}")

# Inicia o bot
bot.run(BOT_TOKEN)