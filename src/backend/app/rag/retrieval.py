from pymilvus import Collection, connections

try:
    from rag.embeddings import gerar_embedding_async
except ModuleNotFoundError:
    from app.rag.embeddings import gerar_embedding_async

async def buscar_similares(pergunta: str, top_k=3):
    connections.connect(host="milvus", port="19530")
    collection = Collection("anomalias_3w")
    collection.load()

    emb_pergunta = [await gerar_embedding_async(pergunta)]
    results = collection.search(
        data=emb_pergunta,
        anns_field="embedding",
        param={"metric_type": "L2", "params": {"nprobe": 10}},
        limit=top_k,
        output_fields=["well", "timestamp", "sensor_data", "evento"],
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

    return "\n".join(contextos)
