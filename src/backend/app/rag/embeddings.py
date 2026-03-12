import os
from typing import List

import httpx


OLLAMA_EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://ollama:11434/api/embed")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_EMBED_TIMEOUT = float(os.getenv("OLLAMA_EMBED_TIMEOUT", "180"))
OLLAMA_EMBED_BATCH_SIZE = int(os.getenv("OLLAMA_EMBED_BATCH_SIZE", "32"))


async def gerar_embedding_async(texto: str) -> List[float]:
    async with httpx.AsyncClient(timeout=OLLAMA_EMBED_TIMEOUT) as client:
        # Ollama atual: /api/embed com lista em `input`.
        r = await client.post(OLLAMA_EMBED_URL, json={"model": OLLAMA_EMBED_MODEL, "input": [texto]})
        if r.status_code < 400:
            body = r.json()
            if "embeddings" in body and body["embeddings"]:
                return body["embeddings"][0]
        # Compatibilidade com endpoint antigo.
        fallback_url = OLLAMA_EMBED_URL.replace("/api/embed", "/api/embeddings")
        r = await client.post(fallback_url, json={"model": OLLAMA_EMBED_MODEL, "prompt": texto})
        r.raise_for_status()
        body = r.json()
        return body["embedding"]


def gerar_embeddings_batch(textos: List[str]) -> List[List[float]]:
    with httpx.Client(timeout=OLLAMA_EMBED_TIMEOUT) as client:
        fallback_url = OLLAMA_EMBED_URL.replace("/api/embed", "/api/embeddings")
        embeddings: List[List[float]] = []
        for i in range(0, len(textos), OLLAMA_EMBED_BATCH_SIZE):
            chunk = textos[i : i + OLLAMA_EMBED_BATCH_SIZE]
            r = client.post(OLLAMA_EMBED_URL, json={"model": OLLAMA_EMBED_MODEL, "input": chunk})
            if r.status_code < 400:
                body = r.json()
                if "embeddings" in body:
                    embeddings.extend(body["embeddings"])
                    continue

            for texto in chunk:
                resp = client.post(fallback_url, json={"model": OLLAMA_EMBED_MODEL, "prompt": texto})
                resp.raise_for_status()
                body = resp.json()
                embeddings.append(body["embedding"])
        return embeddings
