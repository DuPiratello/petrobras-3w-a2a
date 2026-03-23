try:
    from rag.retrieval import buscar_similares
    from utils.ollama_client import query_ollama
except ModuleNotFoundError:
    from app.rag.retrieval import buscar_similares
    from app.utils.ollama_client import query_ollama


async def responder_anomalias(pergunta: str) -> str:
    # 1. Buscar contexto relevante no Milvus
    contextos = await buscar_similares(pergunta, top_k=3)

    # Se o contexto vetorial estiver indisponivel, nao deixar o LLM "improvisar".
    if (
        "Contexto indisponivel" in contextos
        or "Nenhum contexto relevante encontrado" in contextos
    ):
        return (
            "No momento nao consigo responder com base no 3W porque o contexto RAG "
            "nao esta disponivel. "
            f"Detalhe: {contextos} "
            "Acoes recomendadas: subir servicos de RAG (Milvus/MinIO/etcd) e "
            "executar a ingestao do dataset 3W."
        )

    # 2. Montar prompt com contexto
    prompt = f"""Você é um especialista em anomalias em poços de petróleo. Use o contexto abaixo para responder à pergunta.

Contexto:
{contextos}

Pergunta: {pergunta}

Resposta baseada apenas no contexto.
Regras obrigatorias:
- Nao invente informacoes.
- Se o contexto nao trouxer evidencias suficientes, responda exatamente:
  Nao encontrei evidencia suficiente no contexto recuperado para responder com confianca."""
    
    return await query_ollama(prompt)
