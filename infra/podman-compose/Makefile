.PHONY: help config up up-clean check-up down restart ps status doctor logs logs-fastapi logs-gradio logs-milvus \
	mvp-up rag-up data-up rag-all-up build rebuild \
	ollama-pull-embed ingest ingest-max-rows ingest-max-files ingest-path \
	health chat-test dataset-check

SHELL := /bin/bash

# Este Makefile foi pensado para execucao a partir de infra/podman-compose.
COMPOSE_FILE := podman-compose.yml
PODMAN_COMPOSE := podman-compose -f $(COMPOSE_FILE)
PROJECT_LABEL := io.podman.compose.project=podman-compose
UP_LOG := /tmp/podman-compose-up.log
DOWN_LOG := /tmp/podman-compose-down.log
REQUIRED_CONTAINERS := ollama fastapi gradio minio postgres etcd minio-milvus milvus

# Nomes default dos containers gerados pelo podman-compose.
# Ajuste se o prefixo do projeto mudar.
FASTAPI_CONTAINER ?= fastapi
OLLAMA_CONTAINER ?= ollama

# Parametros opcionais para targets de ingestao
MAX_ROWS ?= 2000
MAX_FILES ?= 50
PARQUET_PATH ?= /app/3W/dataset/0/WELL-00001_20170201010207.parquet
CHAT_TEXT ?= Houve alguma anomalia no poco A? Mostre contexto.

help:
	@echo "Targets disponiveis:"
	@echo "  make up              - sobe stack completa (MVP + dados + RAG)"
	@echo "  make up-clean        - sobe stack completa com saida resumida"
	@echo "  make check-up        - valida se todos os servicos criticos estao running"
	@echo "  make mvp-up          - sobe ollama + fastapi + gradio (com build)"
	@echo "  make data-up         - sobe minio + mc + postgres"
	@echo "  make rag-up          - sobe etcd + minio-milvus + milvus"
	@echo "  make down            - derruba todos os servicos"
	@echo "  make restart         - down + up"
	@echo "  make ps              - lista containers ativos"
	@echo "  make status          - lista containers do projeto (ativos e parados)"
	@echo "  make doctor          - diagnostico rapido de portas ocupadas"
	@echo "  make logs            - logs de todos os servicos"
	@echo "  make logs-fastapi    - logs somente do fastapi"
	@echo "  make logs-gradio     - logs somente do gradio"
	@echo "  make logs-milvus     - logs somente do milvus"
	@echo "  make config          - valida e imprime compose resolvido"
	@echo "  make ollama-pull-embed - baixa modelo de embedding no Ollama"
	@echo "  make ingest          - ingestao completa do dataset 3W"
	@echo "  make ingest-max-rows MAX_ROWS=2000"
	@echo "  make ingest-max-files MAX_FILES=50"
	@echo "  make ingest-path PARQUET_PATH=/app/3W/dataset/0/arquivo.parquet"
	@echo "  make dataset-check   - valida se o dataset esta montado no fastapi"
	@echo "  make health          - testa /health da API"
	@echo "  make chat-test CHAT_TEXT='sua pergunta'"

config:
	$(PODMAN_COMPOSE) config

build:
	$(PODMAN_COMPOSE) build

rebuild:
	$(PODMAN_COMPOSE) build --no-cache

mvp-up:
	$(PODMAN_COMPOSE) up -d --build ollama fastapi gradio

data-up:
	$(PODMAN_COMPOSE) up -d minio mc postgres

rag-up:
	$(PODMAN_COMPOSE) up -d etcd minio-milvus milvus

rag-all-up: data-up rag-up

up: mvp-up rag-all-up

up-clean:
	@echo "[1/3] Subindo MVP (ollama, fastapi, gradio)..."
	@$(PODMAN_COMPOSE) up -d --build ollama fastapi gradio >$(UP_LOG) 2>&1 || (echo "Falha no MVP. Ultimas linhas:" && tail -n 40 $(UP_LOG) && exit 1)
	@echo "[2/3] Subindo dados (minio, mc, postgres)..."
	@$(PODMAN_COMPOSE) up -d minio mc postgres >$(UP_LOG) 2>&1 || (echo "Falha na camada de dados. Ultimas linhas:" && tail -n 40 $(UP_LOG) && exit 1)
	@echo "[3/3] Subindo RAG (etcd, minio-milvus, milvus)..."
	@$(PODMAN_COMPOSE) up -d etcd minio-milvus milvus >$(UP_LOG) 2>&1 || (echo "Falha na camada RAG. Ultimas linhas:" && tail -n 40 $(UP_LOG) && exit 1)
	@echo ""
	@echo "Resumo dos containers do projeto:"
	@$(MAKE) --no-print-directory status
	@echo ""
	@$(MAKE) --no-print-directory check-up

down:
	@echo "Derrubando servicos do projeto..."
	@$(PODMAN_COMPOSE) down --remove-orphans >$(DOWN_LOG) 2>&1 || (echo "Falha ao derrubar stack. Ultimas linhas:" && tail -n 40 $(DOWN_LOG) && exit 1)
	@restos="$$(podman ps -aq --filter label=$(PROJECT_LABEL))"; \
	if [ -n "$$restos" ]; then \
		echo "Removendo containers remanescentes do projeto..."; \
		podman rm -f $$restos >/dev/null; \
	fi
	@echo ""
	@echo "Resumo apos down:"
	@$(MAKE) --no-print-directory status

restart: down up

ps:
	podman ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"

status:
	podman ps -a --filter label=$(PROJECT_LABEL) --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

check-up:
	@falhas=""; \
	for c in $(REQUIRED_CONTAINERS); do \
		st=$$(podman inspect -f '{{.State.Status}}' $$c 2>/dev/null || echo missing); \
		if [ "$$st" != "running" ]; then \
			falhas="$$falhas $$c($$st)"; \
		fi; \
	done; \
	if [ -n "$$falhas" ]; then \
		echo "ERRO: servicos nao ficaram running:$$falhas"; \
		echo "Dica: rode 'make doctor' para diagnosticar conflito de portas."; \
		exit 1; \
	fi; \
	echo "OK: todos os servicos criticos estao running."

doctor:
	@echo "Containers do projeto:"
	@podman ps -a --filter label=$(PROJECT_LABEL) --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "Portas escutando no host (8000/7860/9000/9001/9002/9003/19530/5432/11435):"
	@ss -ltnp | rg ':(8000|7860|9000|9001|9002|9003|19530|5432|11435)\b' || true

logs:
	$(PODMAN_COMPOSE) logs -f

logs-fastapi:
	$(PODMAN_COMPOSE) logs -f fastapi

logs-gradio:
	$(PODMAN_COMPOSE) logs -f gradio

logs-milvus:
	$(PODMAN_COMPOSE) logs -f milvus

ollama-pull-embed:
	podman exec -it $(OLLAMA_CONTAINER) ollama pull nomic-embed-text

dataset-check:
	podman exec -it $(FASTAPI_CONTAINER) ls -lah /app/3W/dataset | head

ingest:
	podman exec -it $(FASTAPI_CONTAINER) python /app/rag/ingestao_3w.py

ingest-max-rows:
	podman exec -it -e INGEST_MAX_ROWS=$(MAX_ROWS) $(FASTAPI_CONTAINER) python /app/rag/ingestao_3w.py

ingest-max-files:
	podman exec -it -e INGEST_MAX_FILES=$(MAX_FILES) $(FASTAPI_CONTAINER) python /app/rag/ingestao_3w.py

ingest-path:
	podman exec -it -e DATASET_3W_PARQUET=$(PARQUET_PATH) $(FASTAPI_CONTAINER) python /app/rag/ingestao_3w.py

health:
	curl -s http://localhost:8000/health

chat-test:
	curl -s http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"texto\":\"$(CHAT_TEXT)\"}"
