# Runbook MVP e RAG 3W

Este runbook descreve operacao do sistema focado no dataset 3W.

## 1) MVP Conversacional (Gradio + FastAPI + Ollama)

### Subir servicos
```bash
cd /home/piratello/Desktop/AI Projects/Petrobras3w/infra/podman-compose
podman-compose -f podman-compose.yml up -d --build ollama fastapi gradio
```

### Verificar status
```bash
podman ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

### Endpoints
- Gradio: `http://localhost:7860`
- FastAPI health: `http://localhost:8000/health`

## 2) RAG 3W Basico (Milvus + embeddings)

### Subir dependencias do RAG
```bash
cd /home/piratello/Desktop/AI Projects/Petrobras3w/infra/podman-compose
podman-compose -f podman-compose.yml up -d etcd minio-milvus milvus
```

### Baixar modelo de embedding no Ollama
```bash
podman exec -it ollama ollama pull nomic-embed-text
```

### Ingestao 3W
Por padrao o script procura `.parquet` em:
- `/app/3W/dataset/**.parquet`
- `/app/data/3W/dataset/**.parquet`
- `3W/dataset/**.parquet` (relativo)

Executar ingestao completa:
```bash
podman exec -it fastapi python /app/rag/ingestao_3w.py
```

Limitar por linhas por arquivo:
```bash
podman exec -it -e INGEST_MAX_ROWS=2000 fastapi python /app/rag/ingestao_3w.py
```

Limitar por quantidade de arquivos:
```bash
podman exec -it -e INGEST_MAX_FILES=50 fastapi python /app/rag/ingestao_3w.py
```

Forcar caminho especifico:
```bash
podman exec -it -e DATASET_3W_PARQUET=/app/3W/dataset/0/WELL-00001_20170201010207.parquet fastapi python /app/rag/ingestao_3w.py
```

## 3) Criterios de Sucesso da Ingestao
A execucao so deve ser considerada valida quando houver, no log:
- total de arquivos processados,
- total de linhas/chunks inseridos,
- distribuicao por `class` (incluindo transientes quando presentes),
- contabilizacao explicita de `class/state = null`.

## 4) Politica Minima de Rotulos (escopo 3W)
- `0..9`: classes principais do 3W.
- `101..109`: transientes (offset +100).
- `null` em `class/state`: nao ignorar silenciosamente; registrar e aplicar regra explicita de ingestao.

## 5) Teste via API
```bash
curl -s http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"texto":"Houve alguma anomalia no poco A? Mostre contexto."}'
```

## 6) Troubleshooting Rapido

### Ver logs FastAPI
```bash
cd /home/piratello/Desktop/AI Projects/Petrobras3w/infra/podman-compose
podman-compose -f podman-compose.yml logs -f fastapi
```

### Ver logs Gradio
```bash
cd /home/piratello/Desktop/AI Projects/Petrobras3w/infra/podman-compose
podman-compose -f podman-compose.yml logs -f gradio
```

### Ver logs Milvus
```bash
cd /home/piratello/Desktop/AI Projects/Petrobras3w/infra/podman-compose
podman-compose -f podman-compose.yml logs -f milvus
```

### Validar montagem do dataset no container
```bash
podman exec -it fastapi ls -lah /app/3W/dataset | head
```
