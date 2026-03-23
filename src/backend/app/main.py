from fastapi import FastAPI
from pydantic import BaseModel
try:
    from agents import orchestrator, anomalias, qualidade_dados, desempenho_operacional
except ModuleNotFoundError:
    from app.agents import orchestrator, anomalias, qualidade_dados, desempenho_operacional

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
    elif agente == "qualidade_dados":
        resp = await qualidade_dados.responder_qualidade_dados(pergunta.texto)
    elif agente == "desempenho_operacional":
        resp = await desempenho_operacional.responder_desempenho_operacional(pergunta.texto)
    else:
        # Fallback conservador: manter no escopo 3W.
        agente = "anomalias"
        resp = await anomalias.responder_anomalias(pergunta.texto)

    return Resposta(texto=resp, agente=agente)

@app.get("/health")
async def health():
    return {"status": "ok"}
