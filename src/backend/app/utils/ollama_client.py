import httpx
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.containers.internal:11434/v1/completions")

async def query_ollama(prompt: str, model: str = "llama3.2:1b") -> str:
    async with httpx.AsyncClient() as client:
        payload = {
            "model": model,
            "prompt": prompt,
        }
        response = await client.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            # Ollama /v1/completions returns {"choices": [{"text": "..."}, ...]}
            if isinstance(data, dict):
                choices = data.get("choices")
                if isinstance(choices, list) and len(choices) > 0:
                    first = choices[0]
                    if isinstance(first, dict) and "text" in first:
                        return first.get("text", "")
            return str(data)
        else:
            return f"Erro: {response.status_code} - {response.text}"