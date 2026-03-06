import os
import gradio as gr
import httpx
import asyncio

# When running in container, localhost points to the same container, not the FastAPI service.
# Override via environment variable in compose (e.g. API_URL=http://fastapi:8000/chat)
API_URL = os.environ.get("API_URL", "http://localhost:8000/chat")

async def enviar(pergunta):
    async with httpx.AsyncClient() as client:
        resp = await client.post(API_URL, json={"texto": pergunta})
        if resp.status_code == 200:
            data = resp.json()
            return f"{data['agente']}: {data['texto']}"
        else:
            return f"Erro: {resp.status_code}"

with gr.Blocks() as demo:
    gr.Markdown("# Chat A2A com dados 3W petrobras")
    with gr.Row():
        inp = gr.Textbox(label="Digite sua pergunta")
        out = gr.Markdown("Resposta")
    btn = gr.Button("Enviar")
    btn.click(fn=lambda p: asyncio.run(enviar(p)), inputs=inp, outputs=out)
    
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)