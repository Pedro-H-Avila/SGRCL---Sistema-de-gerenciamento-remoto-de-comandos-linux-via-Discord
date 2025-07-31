# agent.py
# Agente Linux que roda em máquinas Ubuntu 22.04.
# Registra a máquina, faz polling para comandos pendentes e executa scripts.

import aiohttp
import asyncio
import subprocess
import uuid
import os
import time
from dotenv import load_dotenv
# import socket

# # Carrega variáveis de ambiente
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")
def get_unique_machine_name():
    base_name = os.getenv("MACHINE_NAME_BASE", "maquina")
    hostname = socket.gethostname()
    return f"{base_name}_{hostname}"

MACHINE_NAME = get_unique_machine_name()
# Carrega variáveis de ambiente
# load_dotenv()
# API_URL = os.getenv("API_URL", "http://localhost:8000")
# MACHINE_NAME = os.getenv("MACHINE_NAME", "maquina1")
# MACHINE_ID = os.getenv("MACHINE_ID", str(uuid.uuid4()))

# Função para registrar a máquina no servidor
async def register_machine():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/register_machine", json={"id": MACHINE_ID, "name": MACHINE_NAME}) as resp:
            if resp.status == 200:
                print(f"Máquina {MACHINE_NAME} registrada com sucesso")
            else:
                print(f"Erro ao registrar máquina: {resp.status}")

# Função para executar um comando e capturar a saída
def run_command(script_content):
    try:
        result = subprocess.run(script_content, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Erro: Comando excedeu o tempo limite de 30 segundos"
    except Exception as e:
        return f"Erro ao executar comando: {str(e)}"

# Função para verificar e executar comandos pendentes
async def check_commands():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/commands/{MACHINE_ID}") as resp:
            if resp.status == 200:
                commands = await resp.json()
                for command in commands:
                    script = await get_script(command["script_name"])
                    if script:
                        output = run_command(script)
                        await send_result(command["id"], output)

# Função para obter o conteúdo de um script
async def get_script(script_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/scripts/{script_name}") as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["content"]
            return None

# Função para enviar o resultado de um comando
async def send_result(command_id, output):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/commands/{command_id}/result", json={"output": output}) as resp:
            if resp.status == 200:
                print(f"Resultado do comando {command_id} enviado com sucesso")
            else:
                print(f"Erro ao enviar resultado: {resp.status}")

# Loop principal: registra a máquina e verifica comandos a cada 5 minutos
async def main():
    while True:
        await register_machine()
        await check_commands()
        await asyncio.sleep(300)  # 5 minutos

# Inicia o loop
if __name__ == "__main__":
    asyncio.run(main())