# Petrobras3w

Sistema conversacional multiagente com RAG, orientado ao dataset **3W** (Petrobras), executando localmente com Podman.

[![Scope: 3W-only](https://img.shields.io/badge/scope-3W--only-0a7ea4)](#escopo)
[![Runtime: Podman](https://img.shields.io/badge/runtime-podman-892ca0)](#stack-e-arquitetura)
[![API: FastAPI](https://img.shields.io/badge/api-fastapi-009688)](#stack-e-arquitetura)
[![UI: Gradio](https://img.shields.io/badge/ui-gradio-f97316)](#stack-e-arquitetura)
[![Vector DB: Milvus](https://img.shields.io/badge/vector%20db-milvus-00bcd4)](#stack-e-arquitetura)

---

## Indice
- [Escopo](#escopo)
- [Resumo Executivo](#resumo-executivo)
- [Baseline Tecnico do 3W](#baseline-tecnico-do-3w)
- [Stack e Arquitetura](#stack-e-arquitetura)
- [Agentes 3W](#agentes-3w)
- [Status por Requisito](#status-por-requisito)
- [Estrutura do Repositorio](#estrutura-do-repositorio)
- [Setup Rapido](#setup-rapido)
- [Operacao](#operacao)
- [Ingestao 3W](#ingestao-3w)
- [API](#api)
- [Troubleshooting](#troubleshooting)
- [Documentacao](#documentacao)
- [Roadmap Curto](#roadmap-curto)

---

## Escopo
Este repositorio esta **100% focado em 3W**.

Fora do escopo atual:
- consultas corporativas fora do 3W,
- fluxos de negocio nao relacionados a anomalias/desempenho de poco.

---

## Resumo Executivo
- Chat via Gradio consumindo backend FastAPI.
- Orquestrador roteia para agentes especialistas do dominio 3W.
- RAG com embeddings (Ollama) + busca vetorial (Milvus).
- Operacao local via Podman Compose com MinIO/PostgreSQL/Milvus/etcd.

---

## Baseline Tecnico do 3W
| Item | Valor observado |
|---|---|
| Dataset | `3W/dataset` (submodulo) |
| Versao | `2.0.0` |
| Arquivos Parquet | `2228` |
| Volume | `~1.8 GB` |
| Linhas | `~76.6M` |
| Colunas | `30` (`27` variaveis + `class` + `state` + `timestamp`) |
| Classes principais | `0..9` |
| Transientes | `101..109` (offset `+100`) |
| Qualidade critica | ocorrencia de `class/state = null` |

---

## Stack e Arquitetura
### Componentes
| Camada | Tecnologia | Caminho |
|---|---|---|
| UI | Gradio | `src/frontend/app.py` |
| API | FastAPI | `src/backend/app/main.py` |
| Orquestracao | Python | `src/backend/app/agents/orchestrator.py` |
| RAG Ingestao | Pandas + PyMilvus | `src/backend/app/rag/ingestao_3w.py` |
| RAG Retrieval | PyMilvus | `src/backend/app/rag/retrieval.py` |
| Embeddings | Ollama | `src/backend/app/rag/embeddings.py` |
| Infra local | Podman Compose | `infra/podman-compose/podman-compose.yml` |

### Fluxo principal
```text
Gradio -> FastAPI -> Orchestrator -> Agente 3W
                               -> Retrieval (Milvus)
                               -> LLM (Ollama)
```

---

## Agentes 3W
- `anomalias.py`: classes de evento, sintomas e contexto tecnico.
- `qualidade_dados.py`: cobertura, transientes, nulos e consistencia de dados.
- `desempenho_operacional.py`: correlacao de pressao/temperatura/vazao e produtividade.

---

## Status por Requisito
Com base em `docs/requirements analysis.md`.

### Funcionais (RF)
| Requisito | Status |
|---|---|
| RF01 Chat web | Implementado |
| RF02 Orquestracao 3W | Implementado (baseline) |
| RF03 Agente de anomalias | Implementado (baseline) |
| RF04 Agente desempenho operacional | Implementado (baseline) |
| RF05 Pipeline RAG | Implementado (baseline) |
| RF06 EDA/pre-processamento 3W | Parcial |
| RF07 Governanca de rotulos | Parcial |

### Nao Funcionais (RNF)
| Requisito | Status |
|---|---|
| RNF01 Conteinerizacao | Implementado |
| RNF02 Persistencia | Implementado |
| RNF03 Rastreabilidade | Parcial |
| RNF04 Monitoramento operacional | Parcial |
| RNF05 Seguranca backend/orquestrador | Baseline |
| RNF06 Observabilidade de ingestao | Parcial |

---

## Estrutura do Repositorio
```text
Petrobras3w/
├── 3W/                       # submodulo oficial 3W
├── data/                     # persistencia local (milvus, minio-milvus, postgres)
├── docs/
│   ├── project.md
│   ├── requirements analysis.md
│   ├── runbook_mvp_rag.md
│   └── eda_3w_dataset.ipynb
├── infra/
│   └── podman-compose/
│       ├── podman-compose.yml
│       └── Makefile
└── src/
    ├── backend/
    │   └── app/
    │       ├── agents/
    │       ├── rag/
    │       └── utils/
    └── frontend/
```

---

## Setup Rapido
### Pre-requisitos
- Podman
- podman-compose
- curl
- Opcional: Python 3.11+

### 1) Clonar com submodulo 3W
```bash
git clone --recurse-submodules <URL_DO_REPOSITORIO>
cd Petrobras3w
```

Se ja clonou sem submodulo:
```bash
git submodule update --init --recursive
```

### 2) Subir stack
```bash
cd infra/podman-compose
make up-clean
```

### 3) Validar
```bash
make status
make check-up
make health
```

### 4) Acessar
- Gradio: `http://localhost:7860`
- API health: `http://localhost:8000/health`

---

## Operacao
Principais comandos:
```bash
make help
make up
make down
make restart
make logs
make logs-fastapi
make logs-gradio
make logs-milvus
make doctor
```

---

## Ingestao 3W
### Execucao
```bash
# completa
make ingest

# limite por linhas por arquivo
make ingest-max-rows MAX_ROWS=2000

# limite por numero de arquivos
make ingest-max-files MAX_FILES=50

# arquivo/caminho especifico
make ingest-path PARQUET_PATH=/app/3W/dataset/0/WELL-00001_20170201010207.parquet

# checar montagem do dataset no backend
make dataset-check
```

### Politica minima de rotulos
- `0..9`: classes principais.
- `101..109`: transientes.
- `class/state = null`: nao ignorar silenciosamente; registrar e aplicar regra explicita.

### Criterios minimos de sucesso da ingestao
- total de arquivos processados,
- total de registros/chunks inseridos,
- distribuicao por classe,
- contabilizacao de `null`.

---

## API
### `POST /chat`
Request:
```json
{"texto":"Houve alguma anomalia no poco A?"}
```

Response (exemplo):
```json
{"texto":"...resposta...","agente":"anomalias"}
```

Teste rapido:
```bash
make chat-test CHAT_TEXT='Houve alguma anomalia no poco A? Mostre contexto.'
```

---

## Troubleshooting
- Conflito de nomes de container:
  - `make down`
  - limpar remanescentes
  - `make rebuild && make up`
- Sem dataset no container:
  - validar volume `../../3W:/app/3W:ro`
  - `make dataset-check`
- Milvus nao sobe:
  - `make logs-milvus`
  - conferir `etcd` e `minio-milvus`

---

## Documentacao
- [Guia mestre](docs/project.md)
- [Analise de requisitos](docs/requirements%20analysis.md)
- [Runbook MVP + RAG](docs/runbook_mvp_rag.md)
- [EDA](docs/eda_3w_dataset.ipynb)

---

## Roadmap Curto
1. Fechar regra oficial de ingestao para `null` e transientes `101..109`.
2. Publicar metricas estruturadas por execucao de ingestao.
3. Fortalecer testes de regressao (roteamento e retrieval).
4. Evoluir monitoramento operacional e rastreabilidade.

---
Projeto construindo sobre o ecossistema do [3W Petrobras](https://github.com/petrobras/3W).
