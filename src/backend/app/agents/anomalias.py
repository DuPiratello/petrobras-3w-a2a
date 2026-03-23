try:
    from rag.retrieval import buscar_similares
    from utils.ollama_client import query_ollama
except ModuleNotFoundError:
    from app.rag.retrieval import buscar_similares
    from app.utils.ollama_client import query_ollama


async def responder_anomalias(pergunta: str) -> str:
    # 1. Buscar contexto relevante no Milvus
    contextos = await buscar_similares(pergunta, top_k=3)
    
    # 2. Montar prompt com contexto
    prompt = f"""Você é um especialista em anomalias em poços de petróleo. Use o contexto abaixo para responder à pergunta.

Contexto:
{contextos}

Pergunta: {pergunta}

Resposta baseada apenas no contexto (se não houver informação, diga que não encontrou):"""
    
    return await query_ollama(prompt)
