# Runbook MVP e RAG Basico

Este documento descreve os processos e comandos para operar o MVP e habilitar o RAG basico.

## 1) MVP (Gradio + FastAPI + Ollama)

### Subir servicos
```bash
cd /home/piratello/Desktop/AI Projects/Petrobras3w/infra/podman-compose
podman-compose -f podman-compose.yml up -d --build ollama fastapi gradio
```

### Verificar status
```bash
podman ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

### Logs (requisicoes)
```bash
cd /home/piratello/Desktop/AI Projects/Petrobras3w/infra/podman-compose
podman-compose -f podman-compose.yml logs -f fastapi
podman-compose -f podman-compose.yml logs -f gradio
```

### Endpoints
- Gradio: http://localhost:7860
- FastAPI health: http://localhost:8000/health

## 2) RAG Basico (Milvus + embeddings)

### Subir dependencias do RAG
```bash
cd /home/piratello/Desktop/AI Projects/Petrobras3w/infra/podman-compose
podman-compose -f podman-compose.yml up -d etcd minio-milvus milvus
```

### Baixar modelo de embedding no Ollama
```bash
podman exec -it podman-compose_ollama_1 ollama pull nomic-embed-text
```

### Ingestao do dataset 3W
O script procura por `well_A.parquet` em:
- `/app/3W/dataset/well_A/well_A.parquet`
- `/app/data/3W/dataset/well_A/well_A.parquet`
- `3W/dataset/well_A/well_A.parquet` (relativo)

Para executar:
```bash
podman exec -it podman-compose_fastapi_1 python /app/rag/ingestao_3w.py
```

Para limitar a ingestao:
```bash
podman exec -it -e INGEST_MAX_ROWS=2000 podman-compose_fastapi_1 python /app/rag/ingestao_3w.py
```

Para forcar um caminho especifico:
```bash
podman exec -it -e DATASET_3W_PARQUET=/app/3W/dataset/well_A/well_A.parquet \
  podman-compose_fastapi_1 python /app/rag/ingestao_3w.py
```

### Teste via API
```bash
curl -s http://localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"texto":"Houve alguma anomalia no poco A? Mostre contexto."}'
```

## 3) Troubleshooting rapido

### Gradio nao carrega
```bash
cd /home/piratello/Desktop/AI Projects/Petrobras3w/infra/podman-compose
podman-compose -f podman-compose.yml logs -f gradio
```

### Sem dataset dentro do container
```bash
podman exec -it podman-compose_fastapi_1 ls -lah /app/3W/dataset/well_A
```

### Milvus nao sobe
```bash
cd /home/piratello/Desktop/AI Projects/Petrobras3w/infra/podman-compose
podman-compose -f podman-compose.yml logs -f milvus
```

