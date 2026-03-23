# Projeto Petrobras 3W com RAG - Guia Mestre Atualizado

Data de referencia: 2026-03-22

## Objetivo
Construir um sistema conversacional orientado ao **dataset 3W** para apoiar diagnostico tecnico de eventos em pocos, com:
- orquestracao de agentes especialistas no dominio 3W,
- recuperacao de contexto via RAG,
- operacao local em Podman.

## Premissa de Escopo (obrigatoria)
Este projeto esta **100% focado em 3W**. Nao faz parte do escopo atual:
- agente financeiro,
- consultas de dados corporativos fora do 3W,
- fluxos de negocio nao relacionados a operacao/anomalias de poco.

## Baseline Tecnico do 3W (levantamento local)
- Dataset: `3W/dataset` versao `2.0.0`.
- Volume observado: `2228` arquivos Parquet, ~`1.8 GB`.
- Total de linhas observado: ~`76.6M`.
- Estrutura: schema unico com `30` colunas (`27` variaveis + `class` + `state` + `timestamp`).
- Rotulos principais: `0..9`.
- Rotulos transientes observados: `101..109` (offset `+100`).
- Presenca de linhas sem rotulo (`class/state = null`): relevante e deve ser tratada na ingestao.
- Frequencia temporal observada em amostras: `1 Hz`.

## Arquitetura Atual
- `src/frontend/app.py`: interface Gradio.
- `src/backend/app/main.py`: endpoint de chat e health.
- `src/backend/app/agents/`: agentes e orquestrador.
- `src/backend/app/rag/ingestao_3w.py`: ingestao para base vetorial.
- `src/backend/app/rag/embeddings.py`: embeddings via Ollama.
- `src/backend/app/rag/retrieval.py`: busca de contexto.
- `infra/podman-compose/podman-compose.yml`: stack local (Ollama, FastAPI, Gradio, MinIO, PostgreSQL, Milvus, etcd).
- `infra/podman-compose/Makefile`: comandos operacionais.

## Agentes-alvo do Escopo 3W
### 1) Agente de Anomalias 3W
Responsavel por interpretar perguntas sobre classes de evento, sintomas e contexto tecnico.

### 2) Agente de Qualidade de Dados 3W
Responsavel por responder sobre cobertura, distribuicao de classes, transientes e politicas para dados sem rotulo.

### 3) Agente de Desempenho Operacional de Poco
Responsavel por correlacionar sinais de pressao, temperatura e vazao para explicar degradacao operacional.

## Roadmap Atualizado
### Fase A - MVP Conversacional 3W
Status: concluida em base funcional.
- Fluxo `gradio -> fastapi -> ollama` validado.

### Fase B - RAG 3W Basico
Status: em andamento.
- Subir Milvus/MinIO/etcd.
- Executar ingestao 3W.
- Validar resposta com contexto recuperado.

### Fase C - Governanca de Dados 3W
Status: pendente.
- Definir regra explicita para `class/state = null`.
- Definir politica para `101..109` (transientes) no retrieval e na resposta.
- Publicar metricas de ingestao por execucao.

## Regras de Coerencia entre Docs
`docs/requirements analysis.md`, `docs/runbook_mvp_rag.md` e este documento devem permanecer alinhados em:
- escopo 3W,
- agentes suportados,
- criterios de sucesso da ingestao,
- tratamento de rotulos especiais (`null` e `10x`).

## Estrutura de Diretorios (real do repositorio)
```text
Petrobras3w/
├── docs/
├── infra/
│   └── podman-compose/
├── src/
│   ├── backend/
│   │   └── app/
│   │       ├── agents/
│   │       ├── rag/
│   │       └── utils/
│   └── frontend/
├── data/
└── 3W/
```

## Checklist Mestre
- [x] Escopo funcional orientado a 3W definido.
- [x] Baseline tecnico do dataset registrado.
- [x] Stack local com Podman e servicos principais definida.
- [ ] Orquestracao sem agente fora de escopo (remover financeiro do backend).
- [ ] Definicao oficial da politica de ingestao para `null` e `101..109`.
- [ ] Ingestao 3W validada com relatorio de contagem por classe.
- [ ] Agentes 3W (anomalias, qualidade, desempenho) operacionalizados.
