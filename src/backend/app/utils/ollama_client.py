import asyncio
import httpx
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.containers.internal:11434/v1/completions")

async def query_ollama(prompt: str, model: str = "llama3.2:1b") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
    }

    # Avoid immediate failures while Ollama is still booting up.
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(OLLAMA_URL, json=payload)
                if response.status_code != 200:
                    return f"Erro no Ollama: {response.status_code} - {response.text}"

                data = response.json()

                # /v1/completions -> {"choices": [{"text": "..."}]}
                if isinstance(data, dict):
                    choices = data.get("choices")
                    if isinstance(choices, list) and choices:
                        first = choices[0]
                        if isinstance(first, dict) and "text" in first:
                            return str(first.get("text", "")).strip()

                    # /api/generate -> {"response": "..."}
                    if "response" in data:
                        return str(data.get("response", "")).strip()

                return str(data)
        except httpx.HTTPError as exc:
            if attempt == 2:
                return f"Erro de conexao com Ollama ({OLLAMA_URL}): {exc}"
            await asyncio.sleep(1.5 * (attempt + 1))
