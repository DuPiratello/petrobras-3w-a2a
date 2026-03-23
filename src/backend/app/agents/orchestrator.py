try:
    from utils.ollama_client import query_ollama
except ModuleNotFoundError:
    from app.utils.ollama_client import query_ollama

async def decidir_agente(pergunta: str) -> str:
    prompt = f"""Você é um orquestrador de agentes focado exclusivamente no dataset 3W.
Retorne apenas UMA palavra entre:
- 'anomalias' (classes de evento, sensores, falhas, diagnostico),
- 'qualidade_dados' (distribuicao de classes, transientes 101..109, dados nulos, cobertura),
- 'desempenho_operacional' (pressao, temperatura, vazao, produtividade do poco).
Se houver duvida, retorne 'anomalias'.

Pergunta: {pergunta}
Resposta:"""
    resposta = await query_ollama(prompt)
    resposta = resposta.strip().lower()
    if "anomalias" in resposta:
        return "anomalias"
    if "qualidade_dados" in resposta:
        return "qualidade_dados"
    if "desempenho_operacional" in resposta:
        return "desempenho_operacional"
    return "anomalias"
