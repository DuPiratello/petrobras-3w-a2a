from pymilvus import Collection, connections, utility #type: ignore
from pymilvus.exceptions import MilvusException #type: ignore

try:
    from rag.embeddings import gerar_embedding_async
except ModuleNotFoundError:
    from app.rag.embeddings import gerar_embedding_async

async def buscar_similares(pergunta: str, top_k=3):
    try:
        connections.connect(host="milvus", port="19530")
    except MilvusException as exc:
        return (
            "Contexto indisponivel no momento: nao foi possivel conectar ao Milvus. "
            f"Detalhe tecnico: {exc}"
        )

    if not utility.has_collection("anomalias_3w"):
        return (
            "Contexto indisponivel no momento: colecao 'anomalias_3w' nao encontrada. "
            "Execute a ingestao 3W antes de consultar."
        )

    collection = Collection("anomalias_3w")
    collection.load()

    emb_pergunta = [await gerar_embedding_async(pergunta)]
    try:
        results = collection.search(
            data=emb_pergunta,
            anns_field="embedding",
            param={"metric_type": "L2", "params": {"nprobe": 10}},
            limit=top_k,
            output_fields=["well", "timestamp", "sensor_data", "evento"],
        )
    except MilvusException as exc:
        return (
            "Contexto indisponivel no momento: falha na busca vetorial no Milvus. "
            f"Detalhe tecnico: {exc}"
        )

    contextos = []
    for hits in results:
        for hit in hits:
            contextos.append(
                f"Poco: {hit.entity.get('well')} | "
                f"Timestamp: {hit.entity.get('timestamp')} | "
                f"Evento: {hit.entity.get('evento')} | "
                f"Dados: {hit.entity.get('sensor_data')}"
            )

    if not contextos:
        return "Nenhum contexto relevante encontrado no indice vetorial."
    return "\n".join(contextos)
