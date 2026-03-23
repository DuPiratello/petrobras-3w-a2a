try:
    from rag.retrieval import buscar_similares
    from utils.ollama_client import query_ollama
except ModuleNotFoundError:
    from app.rag.retrieval import buscar_similares
    from app.utils.ollama_client import query_ollama


async def responder_desempenho_operacional(pergunta: str) -> str:
    contextos = await buscar_similares(pergunta, top_k=3)
    prompt = f"""Você é um especialista em desempenho operacional de poços no contexto 3W.
Correlacione sinais de pressão, temperatura e vazão para explicar comportamento
operacional e possíveis perdas de produtividade.

Contexto:
{contextos}

Pergunta: {pergunta}

Resposta objetiva e técnica, baseada apenas no contexto. Se não houver evidência,
diga explicitamente que não encontrou dados suficientes."""
    return await query_ollama(prompt)
