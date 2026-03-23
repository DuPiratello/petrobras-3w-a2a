try:
    from rag.retrieval import buscar_similares
    from utils.ollama_client import query_ollama
except ModuleNotFoundError:
    from app.rag.retrieval import buscar_similares
    from app.utils.ollama_client import query_ollama


async def responder_qualidade_dados(pergunta: str) -> str:
    contextos = await buscar_similares(pergunta, top_k=3)
    prompt = f"""Você é um especialista em qualidade de dados do dataset 3W.
Considere cobertura, distribuição de classes, classes transitórias (101..109)
e impacto de class/state nulo.

Contexto:
{contextos}

Pergunta: {pergunta}

Resposta objetiva e técnica, baseada apenas no contexto. Se não houver evidência,
diga explicitamente que não encontrou dados suficientes."""
    return await query_ollama(prompt)
