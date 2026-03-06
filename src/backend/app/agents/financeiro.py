from utils.ollama_client import query_ollama

async def responder_financeiro(pergunta: str) -> str:
    dados = {"orcamento_restante": 500000}
    prompt = f"""Especialista financeiro. Dados: {dados}. Responda.
Pergunta: {pergunta}"""
    return await query_ollama(prompt)