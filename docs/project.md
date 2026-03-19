# 🚀 Projeto A2A com RAG e MLOps - Guia Mestre

Este documento contém todo o planejamento, arquitetura, ferramentas e passos para a construção de um sistema de **agentes de IA (A2A)** com **RAG**, **controle de acesso**, e **MLOps**, utilizando os dados da **Petrobras 3W**. O objetivo é criar um chatbot empresarial onde colaboradores interagem com agentes especialistas (ex: financeiro, anomalias em poços) com base em seu cargo/departamento, usando apenas fontes internas (bancos de dados e documentos).

## 📌 Índice
- [Visão Geral do Projeto](#visão-geral-do-projeto)
- [Arquitetura Completa](#arquitetura-completa)
- [Tecnologias e Ferramentas](#tecnologias-e-ferramentas)
- [Estrutura de Diretórios](#estrutura-de-diretórios)
- [Configuração Inicial (Ambiente)](#configuração-inicial-ambiente)
- [Fase 1: MVP (A2A Lógico)](#fase-1-mvp-a2a-lógico)
- [Fase 2: Adicionar Dados Reais (RAG + Bancos)](#fase-2-adicionar-dados-reais-rag--bancos)
- [Fase 3: MLOps e Monitoramento](#fase-3-mlops-e-monitoramento)
- [Integração com Dataset 3W](#integração-com-dataset-3w)
- [Comandos Úteis e Troubleshooting](#comandos-úteis-e-troubleshooting)
- [Referências e Documentação](#referências-e-documentação)

---

## 🎯 Visão Geral do Projeto

**Problema:** Colaboradores precisam de respostas rápidas e precisas baseadas em dados internos da empresa, com segurança (acesso por cargo) e rastreabilidade.

**Solução:** Um sistema multiagente (A2A) onde:
- Um **agente orquestrador** recebe a pergunta, verifica permissões e decide qual especialista acionar.
- **Agentes especialistas** (ex: financeiro, anomalias de poços) consultam fontes de dados (bancos SQL, documentos) usando **RAG** (Retrieval-Augmented Generation) e geram respostas.
- Toda a lógica roda em **containers Podman** para portabilidade e escalabilidade.
- **MLOps (MLflow)** para versionar prompts, modelos e experimentos.
- **Monitoramento** com Prometheus/Grafana para produção.

**Fonte de dados principal:** [Dataset 3W da Petrobras](https://github.com/petrobras/3W) (dados reais de sensores de poços de petróleo, com eventos indesejáveis).

---

## 🏗️ Arquitetura Completa

```
                    ┌─────────────────────────────────────┐
                    │          CAMADA 5: UI/UX            │
                    │              Gradio                 │
                    └───────────────┬─────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────┐
                    │        CAMADA 4: ORQUESTRAÇÃO       │
                    │              FastAPI                │
                    │(Agente Orquestrador + Especialistas)│
                    └───────────────┬─────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────┐
                    │         CAMADA 3: FERRAMENTAS       │
                    │   ┌─────────────┬─────────────┐     │
                    │   │  PostgreSQL │   Milvus    │     │
                    │   │ (Dados SQL) │(Docs Vetoriais)│  │
                    │   └─────────────┴─────────────┘     │
                    │         ┌─────────────┐             │
                    │         │    MinIO    │             │
                    │         │(Armazenamento)│           │
                    └───────────────┬─────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────┐
                    │      CAMADA 2: PROCESSAMENTO        │
                    │         Pandas / Polars             │
                    │    (Pós-processamento de dados)     │
                    └───────────────┬─────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────┐
                    │         CAMADA 1: CÉREBRO           │
                    │         Ollama + Hugging Face       │
                    │      (Modelos de Linguagem Locais)  │
                    └───────────────┬─────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────┐
                    │      CAMADA 0: INFRAESTRUTURA       │
                    │            Podman                   │
                    │   (Containers + Orquestração Local) │
                    └─────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │         CAMADA MLflow               │
                    │  ┌─────────────────────────────┐    │
                    │  │   MLflow Tracking Server    │    │
                    │  │   (container separado)      │    │
                    │  ├─────────────────────────────┤    │
                    │  │   Backend Store: PostgreSQL │    │
                    │  │   Artifact Store: MinIO     │    │
                    │  │   (pastas mlflow/)          │    │
                    │  └─────────────────────────────┘    │
                    │                                     │
                    │  ┌─────────────────────────────┐    │
                    │  │   O que versionamos:        │    │
                    │  │   • Prompts dos agentes     │    │
                    │  │   • Modelos (embeddings)    │    │
                    │  │   • Métricas de avaliação   │    │
                    │  │   • Parâmetros de chunking  │    │
                    │  └─────────────────────────────┘    │
                    └─────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │         MONITORAMENTO               │
                    │   Prometheus + Grafana + DCGM       │
                    │   (Métricas do sistema + MLflow)    │
                    └─────────────────────────────────────┘
```

---

## 🛠️ Tecnologias e Ferramentas

| Categoria | Ferramenta | Versão | Função |
|:---|:---|:---|:---|
| **Container** | Podman | latest | Gerenciamento de containers (rootless, systemd) |
| **Orquestração local** | podman-compose | latest | Subir múltiplos containers |
| **LLM Local** | Ollama | latest | Modelos de linguagem (ex: llama3.2, phi3) |
| **Embeddings** | Ollama (ou Hugging Face) | - | Gerar embeddings para RAG |
| **Backend API** | FastAPI | 0.115+ | Endpoints para agentes |
| **Interface** | Gradio | 5.x | Chatbot para testes | --> Não escalavel
| **Banco relacional** | PostgreSQL | 15 | Metadados, auditoria, versões |
| **Banco vetorial** | Milvus | 2.4+ | Armazenar e buscar embeddings |
| **Armazenamento objetos** | MinIO | latest | Data Lake (Bronze/Silver/Gold) |
| **Formato tabelas** | Deltalake | 0.9+ | Camadas de dados sobre MinIO |
| **Processamento** | Pandas / Polars | latest | Manipulação de dados |
| **MLOps** | MLflow | 2.16+ | Tracking, versionamento |
| **Monitoramento** | Prometheus + Grafana | latest | Métricas e dashboards |
| **Monitoramento GPU** | DCGM NVIDIA | 3.3+ | Uso de GPU |
| **Dataset** | 3W Petrobras | - | Dados de poços |
| ver sobre RAGAS, 
| lembrar que o milvus, mlflow(criar bucket para armazenar dados de treino), minIO tem interface
| Ver estrutura de dados e tipos de dados do 3W e criar agents específicos para cada função

---

## 📁 Estrutura de Diretórios

```
projeto-a2a/
├── docs/                       # Documentação e diagramas
├── infra/                      # Configurações de infraestrutura
│   ├── podman-compose/         # Arquivos docker-compose (para podman)
│   │   ├── docker-compose.yml  # Principal
│   │   ├── docker-compose.mlflow.yml
│   │   └── docker-compose.monitoring.yml
│   ├── mlflow/                 # Dockerfile e configs do MLflow
│   └── scripts/                 # Scripts auxiliares (backup, init)
├── data/                        # Dados (montados nos containers)
│   ├── minio/                   # Dados do MinIO (bronze, silver, gold)
│   ├── postgres/                 # Volume PostgreSQL
│   └── milvus/                   # Volume Milvus
├── src/                          # Código fonte
│   ├── backend/                  # FastAPI + agentes
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py           # FastAPI app
│   │   │   ├── agents/           # Lógica dos agentes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── orchestrator.py
│   │   │   │   ├── financeiro.py
│   │   │   │   ├── anomalias.py  # Agente para dados 3W
│   │   │   │   └── base.py
│   │   │   ├── rag/              # Pipeline RAG
│   │   │   │   ├── chunking.py
│   │   │   │   ├── embedding.py
│   │   │   │   ├── retrieval.py
│   │   │   │   └── prompt.py
│   │   │   ├── db/               # Conexões com bancos
│   │   │   ├── mlflow_integration.py
│   │   │   └── utils.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── frontend/                 # Gradio (ou outro)
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── notebooks/                # Jupyter para exploração
│       ├── 3W_exploracao.ipynb
│       └── mlflow_experimentos.ipynb
├── tests/                        # Testes automatizados
├── Makefile                       # Comandos úteis (up, down, logs)
├── README.md                      # Visão geral
└── .env                           # Variáveis de ambiente (não versionado)
```

---

## ⚙️ Configuração Inicial (Ambiente)

### 1. Instalar Podman no Ubuntu

```bash
sudo apt update
sudo apt install -y podman podman-compose
```

Verificar instalação:
```bash
podman --version
podman info
```

### 2. Instalar e testar Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:1b  # modelo pequeno para teste
ollama run llama3.2:1b   # testar interativamente
```

### 3. Clonar repositório do 3W

```bash
git clone https://github.com/petrobras/3W.git ~/projeto-a2a/data/3W
```

### 4. Configurar ambiente Python para exploração (opcional, fora de container)

```bash
cd ~/projeto-a2a
python3 -m venv venv
source venv/bin/activate
pip install jupyter pandas pyarrow
jupyter notebook
```

Abra o notebook em `notebooks/3W_exploracao.ipynb` e explore os dados.

---

## 🧪 Fase 1: MVP (A2A Lógico)

Nesta fase, construímos a lógica de agentes sem dados reais, usando dados simulados e o Ollama para decisões.

### 1.1 Criar estrutura básica do backend

```bash
mkdir -p src/backend/app/agents src/backend/app/utils
touch src/backend/app/__init__.py
```

### 1.2 Criar `src/backend/requirements.txt`

```txt
fastapi
uvicorn
httpx
pydantic
python-multipart
ollama  # cliente Python opcional
```

### 1.3 Criar `src/backend/app/utils/ollama_client.py`

```python
import httpx
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.containers.internal:11434/api/generate")

async def query_ollama(prompt: str, model: str = "llama3.2:1b") -> str:
    async with httpx.AsyncClient() as client:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = await client.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "")
        else:
            return f"Erro: {response.status_code}"
```

### 1.4 Criar `src/backend/app/agents/orchestrator.py`

```python
from ..utils.ollama_client import query_ollama

async def decidir_agente(pergunta: str) -> str:
    prompt = f"""Você é um orquestrador. Analise a pergunta e diga apenas uma palavra: 'anomalias' se for sobre problemas em poços, sensores, eventos; 'financeiro' se for sobre gastos, orçamento; 'geral' caso contrário.
Pergunta: {pergunta}
Resposta:"""
    resposta = await query_ollama(prompt)
    resposta = resposta.strip().lower()
    if "anomalias" in resposta:
        return "anomalias"
    elif "financeiro" in resposta:
        return "financeiro"
    return "geral"
```

### 1.5 Criar `src/backend/app/agents/anomalias.py` (simulado)

```python
from ..utils.ollama_client import query_ollama

async def responder_anomalias(pergunta: str) -> str:
    # Simula consulta a dados
    dados = {"ultima_anomalia": "Fechamento espúrio de DHSV em 2024-01-15"}
    prompt = f"""Você é um especialista em anomalias de poços. Use os dados: {dados} para responder.
Pergunta: {pergunta}
Resposta amigável:"""
    return await query_ollama(prompt)
```

### 1.6 Criar `src/backend/app/agents/financeiro.py` (simulado)

```python
from ..utils.ollama_client import query_ollama

async def responder_financeiro(pergunta: str) -> str:
    dados = {"orcamento_restante": 500000}
    prompt = f"""Especialista financeiro. Dados: {dados}. Responda.
Pergunta: {pergunta}"""
    return await query_ollama(prompt)
```

### 1.7 Criar `src/backend/app/agents/geral.py`

```python
from ..utils.ollama_client import query_ollama

async def responder_geral(pergunta: str) -> str:
    prompt = f"""Assistente geral. Responda de forma educada, mas se não souber, diga que não tem informação.
Pergunta: {pergunta}"""
    return await query_ollama(prompt)
```

### 1.8 Criar `src/backend/app/main.py`

```python
from fastapi import FastAPI
from pydantic import BaseModel
from .agents import orchestrator, anomalias, financeiro, geral

app = FastAPI(title="A2A Orquestrador")

class Pergunta(BaseModel):
    texto: str

class Resposta(BaseModel):
    texto: str
    agente: str

@app.post("/chat", response_model=Resposta)
async def chat(pergunta: Pergunta):
    agente = await orchestrator.decidir_agente(pergunta.texto)
    
    if agente == "anomalias":
        resp = await anomalias.responder_anomalias(pergunta.texto)
    elif agente == "financeiro":
        resp = await financeiro.responder_financeiro(pergunta.texto)
    else:
        resp = await geral.responder_geral(pergunta.texto)
    
    return Resposta(texto=resp, agente=agente)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### 1.9 Criar `src/backend/Dockerfile`

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

ENV OLLAMA_URL=http://host.containers.internal:11434/api/generate

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.10 Criar frontend Gradio `src/frontend/app.py`

```python
import gradio as gr
import httpx
import asyncio

API_URL = "http://fastapi:8000/chat"  # dentro da rede podman

async def enviar(pergunta):
    async with httpx.AsyncClient() as client:
        resp = await client.post(API_URL, json={"texto": pergunta})
        if resp.status_code == 200:
            data = resp.json()
            return f"**Agente:** {data['agente']}\n\n{data['texto']}"
        return f"Erro: {resp.status_code}"

with gr.Blocks() as demo:
    gr.Markdown("# Chatbot A2A com Dados 3W")
    with gr.Row():
        inp = gr.Textbox(label="Pergunta")
        out = gr.Markdown(label="Resposta")
    btn = gr.Button("Enviar")
    btn.click(fn=lambda p: asyncio.run(enviar(p)), inputs=inp, outputs=out)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

### 1.11 `src/frontend/requirements.txt`

```txt
gradio
httpx
```

### 1.12 `src/frontend/Dockerfile`

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
```

### 1.13 Criar `infra/podman-compose/docker-compose.yml` (Fase 1)

```yaml
version: '3.8'

services:
  fastapi:
    build: ../../src/backend
    ports:
      - "8000:8000"
    extra_hosts:
      - "host.containers.internal:host-gateway"
    networks:
      - a2a-net

  gradio:
    build: ../../src/frontend
    ports:
      - "7860:7860"
    depends_on:
      - fastapi
    extra_hosts:
      - "host.containers.internal:host-gateway"
    networks:
      - a2a-net

networks:
  a2a-net:
    driver: bridge
```

### 1.14 Rodar a Fase 1

```bash
cd infra/podman-compose
podman-compose up --build
```

Acesse `http://localhost:7860` e teste perguntas como:
- "Houve alguma anomalia no poço ontem?"
- "Qual o orçamento restante?"
- "Qual é a política de férias?"

---

## 🗃️ Fase 2: Adicionar Dados Reais (RAG + Bancos)

Agora vamos integrar os dados reais do 3W e outros documentos usando MinIO (lake), PostgreSQL (metadados) e Milvus (vetorial).

### 2.1 Configurar MinIO (camadas Bronze/Silver/Gold)

Adicione ao `docker-compose.yml`:

```yaml
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - ../../data/minio:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    networks:
      - a2a-net

  # Inicializar buckets
  mc:
    image: minio/mc:latest
    depends_on:
      - minio
    entrypoint: >
      /bin/sh -c "
      sleep 5;
      /usr/bin/mc config host add myminio http://minio:9000 minioadmin minioadmin;
      /usr/bin/mc mb myminio/bronze --ignore-existing;
      /usr/bin/mc mb myminio/silver --ignore-existing;
      /usr/bin/mc mb myminio/gold --ignore-existing;
      exit 0;
      "
    networks:
      - a2a-net
```

### 2.2 Configurar PostgreSQL (metadados, auditoria)

```yaml
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: a2a
      POSTGRES_PASSWORD: a2a
      POSTGRES_DB: a2a_metadata
    volumes:
      - ../../data/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - a2a-net
```

### 2.3 Configurar Milvus (banco vetorial)

```yaml
  etcd:
    image: quay.io/coreos/etcd:v3.5.5
    command: etcd -advertise-client-urls=http://0.0.0.0:2379 -listen-client-urls=http://0.0.0.0:2379
    networks:
      - a2a-net

  minio-milvus:
    image: minio/minio:latest
    command: server /data --console-address ":9003"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - ../../data/minio-milvus:/data
    ports:
      - "9002:9000"
      - "9003:9001"
    networks:
      - a2a-net

  milvus:
    image: milvusdb/milvus:v2.4.5
    command: ["milvus", "run", "standalone"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio-milvus:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    volumes:
      - ../../data/milvus:/var/lib/milvus
    ports:
      - "19530:19530"
    depends_on:
      - etcd
      - minio-milvus
    networks:
      - a2a-net
```

### 2.4 Ingestão de dados do 3W para o pipeline RAG

Criar script `src/backend/app/rag/ingestao_3w.py`:

```python
import pandas as pd
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Conectar ao Milvus
connections.connect(host='milvus', port='19530')

# Criar coleção se não existir
collection_name = "anomalias_3w"
if not utility.has_collection(collection_name):
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="well", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="timestamp", dtype=DataType.VARCHAR, max_length=30),
        FieldSchema(name="sensor_data", dtype=DataType.VARCHAR, max_length=5000),  # JSON string
        FieldSchema(name="evento", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384)  # Modelo pequeno
    ]
    schema = CollectionSchema(fields, description="Dados 3W")
    collection = Collection(name=collection_name, schema=schema)
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
else:
    collection = Collection(name=collection_name)

# Carregar dados do 3W (exemplo: well_A.parquet)
df = pd.read_parquet("data/3W/dataset/well_A/well_A.parquet")

# Gerar embeddings para cada linha (ex: concatenar colunas de sensores)
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dim
textos = df.apply(lambda row: f"Well {row['well']} at {row['timestamp']} sensors: {row.drop(['well','timestamp','evento']).to_dict()}", axis=1).tolist()
embeddings = model.encode(textos).tolist()

# Inserir no Milvus
insert_data = [
    df['well'].tolist(),
    df['timestamp'].astype(str).tolist(),
    df.drop(['well','timestamp','evento'], axis=1).to_json(orient='records'),  # simplificado
    df['evento'].fillna('normal').tolist(),
    embeddings
]
collection.insert(insert_data)
collection.flush()
print(f"Inseridos {len(df)} registros")
```

### 2.5 Atualizar agente de anomalias para usar RAG

Em `src/backend/app/agents/anomalias.py`:

```python
from ..rag.retrieval import buscar_similares
from ..utils.ollama_client import query_ollama

async def responder_anomalias(pergunta: str) -> str:
    # 1. Buscar contexto relevante no Milvus
    contextos = await buscar_similares(pergunta, top_k=3)
    
    # 2. Montar prompt com contexto
    prompt = f"""Você é um especialista em anomalias em poços de petróleo. Use o contexto abaixo para responder à pergunta.

Contexto:
{contextos}

Pergunta: {pergunta}

Resposta baseada apenas no contexto (se não houver informação, diga que não encontrou):"""
    
    return await query_ollama(prompt)
```

E criar `src/backend/app/rag/retrieval.py`:

```python
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

async def buscar_similares(pergunta: str, top_k=3):
    connections.connect(host='milvus', port='19530')
    collection = Collection("anomalias_3w")
    collection.load()
    
    # Embedding da pergunta
    emb_pergunta = model.encode([pergunta]).tolist()
    
    # Busca
    results = collection.search(
        data=emb_pergunta,
        anns_field="embedding",
        param={"metric_type": "L2", "params": {"nprobe": 10}},
        limit=top_k,
        output_fields=["well", "timestamp", "sensor_data", "evento"]
    )
    
    contextos = []
    for hits in results:
        for hit in hits:
            contextos.append(f"Poço: {hit.entity.get('well')} | Timestamp: {hit.entity.get('timestamp')} | Evento: {hit.entity.get('evento')} | Dados: {hit.entity.get('sensor_data')}")
    
    return "\n".join(contextos)
```

### 2.6 Atualizar docker-compose para incluir novos serviços

Adicione os serviços acima ao `docker-compose.yml` da Fase 1. Lembre-se de ajustar as redes e dependências.

### 2.7 Rodar ingestão inicial

Crie um container temporário para executar o script de ingestão:

```bash
podman run --rm --network a2a-net -v $(pwd)/../../src:/app -w /app python:3.10-slim bash -c "pip install pymilvus pandas sentence-transformers && python rag/ingestao_3w.py"
```

Ou adicione um serviço no compose para isso.

---

## 📈 Fase 3: MLOps e Monitoramento

### 3.1 Configurar MLflow com PostgreSQL e MinIO

Adicione ao `docker-compose.yml`:

```yaml
  mlflow:
    build: ../../infra/mlflow
    ports:
      - "5000:5000"
    environment:
      MLFLOW_S3_ENDPOINT_URL: http://minio:9000
      AWS_ACCESS_KEY_ID: minioadmin
      AWS_SECRET_ACCESS_KEY: minioadmin
    command: >
      mlflow server
      --backend-store-uri postgresql://a2a:a2a@postgres/mlflow
      --default-artifact-root s3://mlflow/
      --host 0.0.0.0
      --port 5000
    depends_on:
      - postgres
      - minio
    networks:
      - a2a-net
```

Crie `infra/mlflow/Dockerfile`:

```dockerfile
FROM python:3.10-slim
RUN pip install mlflow boto3 psycopg2-binary
EXPOSE 5000
```

E um serviço para criar bucket `mlflow` no MinIO (adicione ao `mc` ou separado).

### 3.2 Integrar MLflow no código dos agentes

Em `src/backend/app/mlflow_integration.py`:

```python
import mlflow
import os

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("agentes_a2a")

def log_agente_run(agente_nome, prompt, pergunta, resposta, metricas=None):
    with mlflow.start_run(run_name=f"{agente_nome}_{pergunta[:30]}"):
        mlflow.log_param("agente", agente_nome)
        mlflow.log_param("prompt_template", prompt[:500])
        mlflow.log_param("pergunta", pergunta)
        mlflow.log_text(resposta, "resposta.txt")
        if metricas:
            mlflow.log_metrics(metricas)
        mlflow.log_artifact("caminho/para/contexto_usado.txt")  # se houver
```

Modifique `anomalias.py` para logar:

```python
from ..mlflow_integration import log_agente_run

async def responder_anomalias(pergunta: str) -> str:
    contextos = await buscar_similares(pergunta)
    prompt_template = "Você é especialista... Contexto: {contextos} ..."
    prompt = prompt_template.format(contextos=contextos, pergunta=pergunta)
    resposta = await query_ollama(prompt)
    
    # Log no MLflow
    log_agente_run("anomalias", prompt_template, pergunta, resposta, metricas={"tokens": len(resposta.split())})
    
    return resposta
```

### 3.3 Configurar Prometheus + Grafana

Adicione ao compose:

```yaml
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ../../infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - a2a-net

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ../../infra/grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    networks:
      - a2a-net

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    networks:
      - a2a-net
```

Crie `infra/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'podman'
    static_configs:
      - targets: ['host.containers.internal:9323']  # métricas do podman? ou usar node-exporter
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
  - job_name: 'mlflow'
    static_configs:
      - targets: ['mlflow:5000']  # se mlflow expor métricas
```

### 3.4 DCGM para GPU

Se tiver GPU NVIDIA:

```yaml
  dcgm-exporter:
    image: nvidia/dcgm-exporter:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    ports:
      - "9400:9400"
    networks:
      - a2a-net
```

No prometheus.yml, adicione target `dcgm-exporter:9400`.

---

## 🧪 Integração com Dataset 3W

### Notebook de Exploração

Crie `src/notebooks/3W_exploracao.ipynb` com:

1. Carregar parquet com pandas
2. Visualizar séries temporais
3. Estatísticas dos eventos
4. Gerar embeddings para testes

### Exemplo de Uso do Agente de Anomalias

Após a ingestão, perguntas como:
- "Mostre anomalias no poço A nos últimos 30 dias"
- "O que causou o fechamento da DHSV em 2024-01-15?"
- "Houve alguma anomalia com alta pressão?"

O agente usará o RAG para buscar eventos similares no Milvus e responder.

---

## 📝 Comandos Úteis (Makefile)

Crie um `Makefile` na raiz:

```makefile
.PHONY: up down logs build clean

up:
	cd infra/podman-compose && podman-compose up -d

down:
	cd infra/podman-compose && podman-compose down

logs:
	cd infra/podman-compose && podman-compose logs -f

build:
	cd infra/podman-compose && podman-compose build

clean:
	podman system prune -f
```

Use `make up`, `make logs`, etc.

---

## 🆘 Troubleshooting Comum

| Problema | Solução |
|:---|:---|
| `host.containers.internal` não resolve | Use `--add-host host.containers.internal:host-gateway` no `podman run` ou `extra_hosts` no compose |
| MLflow não acessa MinIO | Verifique variáveis de ambiente `MLFLOW_S3_ENDPOINT_URL` e credenciais |
| Milvus não inicia | Verifique se etcd e minio-milvus estão saudáveis |
| Ollama fora do container | Certifique-se que o serviço Ollama está rodando no host (`ollama serve`) |
| Permissão de volumes | Use `podman unshare` para ajustar permissões ou rode como root (não recomendado) |

---

## 📚 Referências

- [Podman Documentation](https://podman.io/docs)
- [Ollama](https://ollama.com/)
- [Milvus](https://milvus.io/)
- [MinIO](https://min.io/)
- [MLflow](https://mlflow.org/)
- [Dataset 3W Petrobras](https://github.com/petrobras/3W)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Gradio](https://gradio.app/)

---

## ✅ Checklist Geral

- [ ] Fase 1 completa (agentes lógicos com Ollama)
- [ ] Fase 2 completa (MinIO, PostgreSQL, Milvus, RAG funcional)
- [ ] Dados 3W ingeridos no Milvus
- [ ] Agente de anomalias usando RAG
- [ ] MLflow integrado e logando experimentos
- [ ] Monitoramento com Prometheus/Grafana
- [ ] Testes de carga e otimizações

---
