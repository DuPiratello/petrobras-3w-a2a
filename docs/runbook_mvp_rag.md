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
Por padrao o script procura arquivos `.parquet` em:
- `/app/3W/dataset/**.parquet`
- `/app/data/3W/dataset/**.parquet`
- `3W/dataset/**.parquet` (relativo)

Para executar (varre tudo):
```bash
podman exec -it podman-compose_fastapi_1 python /app/rag/ingestao_3w.py
```

Para limitar a ingestao por linhas (por arquivo):
```bash
podman exec -it -e INGEST_MAX_ROWS=2000 podman-compose_fastapi_1 python /app/rag/ingestao_3w.py
```

Para limitar a quantidade de arquivos:
```bash
podman exec -it -e INGEST_MAX_FILES=50 podman-compose_fastapi_1 python /app/rag/ingestao_3w.py
```

Para forcar um caminho especifico (arquivo ou diretorio):
```bash
podman exec -it -e DATASET_3W_PARQUET=/app/3W/dataset/0/WELL-00001_20170201010207.parquet \
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
