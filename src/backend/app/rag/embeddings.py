import os
import time
from typing import List

import httpx


OLLAMA_EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://ollama:11434/api/embed")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_EMBED_TIMEOUT = float(os.getenv("OLLAMA_EMBED_TIMEOUT", "180"))
OLLAMA_EMBED_BATCH_SIZE = int(os.getenv("OLLAMA_EMBED_BATCH_SIZE", "32"))
OLLAMA_EMBED_RETRIES = int(os.getenv("OLLAMA_EMBED_RETRIES", "3"))
OLLAMA_EMBED_RETRY_BACKOFF = float(os.getenv("OLLAMA_EMBED_RETRY_BACKOFF", "2"))


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


def _post_with_retries(client: httpx.Client, url: str, payload: dict) -> httpx.Response:
    last_exc: Exception | None = None
    for tentativa in range(1, OLLAMA_EMBED_RETRIES + 1):
        try:
            resp = client.post(url, json=payload)
            return resp
        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ConnectError) as exc:
            last_exc = exc
            if tentativa == OLLAMA_EMBED_RETRIES:
                raise
            time.sleep(OLLAMA_EMBED_RETRY_BACKOFF * tentativa)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("Falha desconhecida ao chamar endpoint de embedding.")


def _embed_single_with_fallback(client: httpx.Client, texto: str, fallback_url: str) -> List[float]:
    resp = _post_with_retries(
        client,
        fallback_url,
        {"model": OLLAMA_EMBED_MODEL, "prompt": texto},
    )
    resp.raise_for_status()
    body = resp.json()
    return body["embedding"]


def gerar_embeddings_batch(textos: List[str]) -> List[List[float]]:
    with httpx.Client(timeout=OLLAMA_EMBED_TIMEOUT) as client:
        fallback_url = OLLAMA_EMBED_URL.replace("/api/embed", "/api/embeddings")
        embeddings: List[List[float]] = []
        for i in range(0, len(textos), OLLAMA_EMBED_BATCH_SIZE):
            chunk = textos[i : i + OLLAMA_EMBED_BATCH_SIZE]
            try:
                r = _post_with_retries(
                    client,
                    OLLAMA_EMBED_URL,
                    {"model": OLLAMA_EMBED_MODEL, "input": chunk},
                )
                if r.status_code < 400:
                    body = r.json()
                    if "embeddings" in body and body["embeddings"]:
                        embeddings.extend(body["embeddings"])
                        continue
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ConnectError):
                pass

            # Fallback seguro: processa item a item para evitar perder progresso em lotes grandes.
            for texto in chunk:
                embeddings.append(_embed_single_with_fallback(client, texto, fallback_url))
        return embeddings
