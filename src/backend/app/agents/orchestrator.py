from utils.ollama_client import query_ollama

async def decidir_agente(pergunta: str) -> str:
    prompt = f"""Você é um orquestrador. Analise a pergunta e diga apenas uma palavra: 'anomalias' se for sobre problemas em poços, sensores, eventos; 'financeiro' se for sobre gastos, orçamento; 'geral' caso contrário.
Pergunta: {pergunta}
Resposta:"""
    resposta = await query_ollama(prompt)
    resposta = resposta.strip().lower()
    if "anomalias" in resposta:
        return "anomalias"
    elif "financeiro" in resposta:
        return "financeiro"
    return "geral"