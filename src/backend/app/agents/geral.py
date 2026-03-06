try:
    from utils.ollama_client import query_ollama
except ModuleNotFoundError:
    from app.utils.ollama_client import query_ollama

async def responder_geral(pergunta: str) -> str:
    prompt = f"""Assistente geral. Responda de forma educada, mas se não souber, diga que não tem informação.
Pergunta: {pergunta}"""
    return await query_ollama(prompt)
