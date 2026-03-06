from fastapi import FastAPI
from pydantic import BaseModel
try:
    from agents import orchestrator, anomalias, financeiro, geral
except ModuleNotFoundError:
    from app.agents import orchestrator, anomalias, financeiro, geral

app = FastAPI(title="A2A Orquestrador")

class Pergunta(BaseModel):
    texto: str

class Resposta(BaseModel):
    texto: str
    agente: str

@app.post("/chat", response_model=Resposta)
async def chat(pergunta: Pergunta):
    agente = await orchestrator.decidir_agente(pergunta.texto)
    
    if agente == "anomalias":
        resp = await anomalias.responder_anomalias(pergunta.texto)
    elif agente == "financeiro":
        resp = await financeiro.responder_financeiro(pergunta.texto)
    else:
        resp = await geral.responder_geral(pergunta.texto)
    
    return Resposta(texto=resp, agente=agente)

@app.get("/health")
async def health():
    return {"status": "ok"}
