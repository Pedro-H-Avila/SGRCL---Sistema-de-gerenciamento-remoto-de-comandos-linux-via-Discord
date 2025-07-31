# server.py
# Serviço web com FastAPI para gerenciar máquinas, scripts e comandos.
# Usa SQLAlchemy para interagir com o banco PostgreSQL.

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import os
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configura o banco de dados com SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo SQLAlchemy para a tabela 'machines'
class Machine(Base):
    __tablename__ = "machines"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    last_seen = Column(Integer, nullable=False)

# Modelo SQLAlchemy para a tabela 'scripts'
class Script(Base):
    __tablename__ = "scripts"
    name = Column(String, primary_key=True)
    content = Column(String, nullable=False)

# Modelo SQLAlchemy para a tabela 'commands'
class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True)
    machine_id = Column(String, nullable=False)
    script_name = Column(String, nullable=False)
    status = Column(String, default="pending")
    output = Column(String)

# Cria as tabelas no banco
Base.metadata.create_all(bind=engine)

# Modelos Pydantic para validação de entrada/saída
class MachineCreate(BaseModel):
    id: str
    name: str

class ScriptCreate(BaseModel):
    name: str
    content: str

class ExecuteCommand(BaseModel):
    machine_name: str
    script_name: str

class CommandResult(BaseModel):
    output: str

# Inicializa o FastAPI
app = FastAPI()

# Endpoint: Lista máquinas ativas (ping nos últimos 5 minutos)
@app.get("/machines")
def list_machines():
    db = SessionLocal()
    try:
        five_minutes_ago = int(time.time()) - 300
        machines = db.query(Machine).filter(Machine.last_seen >= five_minutes_ago).all()
        return [{"id": m.id, "name": m.name} for m in machines]
    finally:
        db.close()

# Endpoint: Registra ou atualiza uma máquina
@app.post("/register_machine")
def register_machine(machine: MachineCreate):
    db = SessionLocal()
    try:
        db_machine = db.query(Machine).filter(Machine.id == machine.id).first()
        if db_machine:
            db_machine.name = machine.name
            db_machine.last_seen = int(time.time())
        else:
            db_machine = Machine(id=machine.id, name=machine.name, last_seen=int(time.time()))
            db.add(db_machine)
        db.commit()
        return {"message": "Máquina registrada com sucesso"}
    finally:
        db.close()

# Endpoint: Cadastra um script
@app.post("/scripts")
def register_script(script: ScriptCreate):
    db = SessionLocal()
    try:
        existing_script = db.query(Script).filter(Script.name == script.name).first()
        if existing_script:
            raise HTTPException(status_code=400, detail="Script já existe")
        db_script = Script(name=script.name, content=script.content)
        db.add(db_script)
        db.commit()
        return {"message": "Script cadastrado com sucesso"}
    finally:
        db.close()

# Endpoint: Agenda um comando
@app.post("/execute")
def execute_command(command: ExecuteCommand):
    db = SessionLocal()
    try:
        machine = db.query(Machine).filter(Machine.name == command.machine_name).first()
        if not machine:
            raise HTTPException(status_code=404, detail="Máquina não encontrada")
        script = db.query(Script).filter(Script.name == command.script_name).first()
        if not script:
            raise HTTPException(status_code=404, detail="Script não encontrado")
        db_command = Command(machine_id=machine.id, script_name=command.script_name, status="pending")
        db.add(db_command)
        db.commit()
        return {"message": "Comando agendado com sucesso"}
    finally:
        db.close()

# Endpoint: Retorna comandos pendentes para uma máquina
@app.get("/commands/{machine_id}")
def get_pending_commands(machine_id: str):
    db = SessionLocal()
    try:
        commands = db.query(Command).filter(Command.machine_id == machine_id, Command.status == "pending").all()
        return [{"id": c.id, "script_name": c.script_name} for c in commands]
    finally:
        db.close()

# Endpoint: Recebe o resultado de um comando
@app.post("/commands/{command_id}/result")
def save_command_result(command_id: int, result: CommandResult):
    db = SessionLocal()
    try:
        command = db.query(Command).filter(Command.id == command_id).first()
        if not command:
            raise HTTPException(status_code=404, detail="Comando não encontrado")
        command.status = "completed"
        command.output = result.output
        db.commit()
        return {"message": "Resultado salvo com sucesso"}
    finally:
        db.close()

# Inicia o servidor (usado pelo Heroku ou localmente)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))