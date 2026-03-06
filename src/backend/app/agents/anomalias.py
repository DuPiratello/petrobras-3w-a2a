try:
    from utils.ollama_client import query_ollama
except ModuleNotFoundError:
    from app.utils.ollama_client import query_ollama

async def responder_anomalias(pergunta: str) -> str:
    # Simula consulta a dados
    dados = {"ultima_anomalia": "Fechamento espúrio de DHSV em 2024-01-15"}
    prompt = f"""Você é um especialista em anomalias de poços. Use os dados: {dados} para responder.
Pergunta: {pergunta}
Resposta amigável:"""
    return await query_ollama(prompt)
