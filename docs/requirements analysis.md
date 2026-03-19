## Requisitos

### ⚙️ Requisitos Funcionais (RF)
Estes requisitos detalham o comportamento do sistema e se conectam diretamente com os diretórios `src/` e `data/`.

***RF01*** **- Interacao de usuario via chatbot**
- Descricao: O sistema deve prover uma interface conversacional web onde o colaborador possa enviar perguntas em linguagem natural.
- Mapeamento: `src/frontend/app.py` (Gradio).
- Classificacao: Essencial.

***RF02*** - **Orquestracao e controle de acesso**
- Descricao: O sistema deve receber a pergunta, identificar o cargo/departamento do colaborador, validar suas permissoes e decidir qual agente sera acionado.
- Mapeamento: `src/backend/app/agents/orchestrator.py` e `db/` (PostgreSQL para validacao).
- Classificacao: Essencial.

***RF03*** **- Consulta especializada em anomalias (Dataset 3W)**
- Descricao: O sistema deve possuir um agente especialista capaz de consultar, interpretar e responder perguntas sobre eventos indesejaveis em pocos de petroleo, baseando-se nos dados reais da Petrobras.
- Mapeamento: `src/backend/app/agents/anomalias.py`.
- Classificacao: Essencial.

***RF04*** **- Consulta especializada financeira**
- Descricao: O sistema deve possuir um agente especialista capaz de consultar e responder a dados financeiros internos.
- Mapeamento: `src/backend/app/agents/financeiro.py`.
- Classificacao: Importante.

***RF05*** **- Processamento RAG (Retrieval-Augmented Generation)**
- Descricao: O sistema deve fatiar documentos (chunking), gerar embeddings, buscar contexto relevante e injetar no prompt do LLM para a resposta final.
- Mapeamento: `src/backend/app/rag/` (`chunking.py`, `embedding.py`, `retrieval.py`, `prompt.py`).
- Classificacao: Essencial.

***RF06*** **- Analise exploratoria (EDA) e pre-processamento de dados (Dataset 3W)**
- Descricao: O projeto deve contemplar a execucao de scripts e notebooks para a extracao, exploracao, identificacao de tipos de dados, limpeza e transformacao dos dados brutos do dataset 3W, preparando-os para o pipeline do RAG e ingestao no banco vetorial.
- Visibilidade: Pode ser classificado como um requisito funcional oculto, visto que toda essa preparacao dos dados sera efetuada pela arquitetura do sistema sem o conhecimento explicito do colaborador que esta interagindo com o chat final.
- Mapeamento: `src/notebooks/3W_exploracao.ipynb` (exploracao) e manipulacao no Data Lake usando Polars/Pandas no MinIO (`data/minio/`).
- Classificacao (necessidade): Essencial. E um requisito imprescindivel sem o qual a consulta ao banco vetorial nao podera entrar em funcionamento.
- Prioridade: Alta (Essencial + Urgente), devendo ser uma das primeiras etapas praticas do cronograma.

### 🛡️ Requisitos Nao Funcionais (RNF)
Estes requisitos impõem restricoes de arquitetura, seguranca e desempenho, relacionando-se profundamente com as tecnologias escolhidas e o diretorio `infra/`.

***RNF01*** **- Restricao de implementacao (Conteinerizacao)**
- Descricao: Todo o ambiente (backend, frontend, bancos e monitoramento) deve ser conteinerizado utilizando a tecnologia Podman (rootless) orquestrada localmente.
- Categoria: Implementacao / Restricoes de hardware e software.
- Mapeamento: `infra/podman-compose/` e Dockerfiles.

***RNF02*** **- Armazenamento e recuperacao eficiente (Persistencia)**
- Descricao: A camada de dados deve suportar busca vetorial de alta performance para o RAG e armazenamento em data lake (Bronze, Silver, Gold) para os dados brutos/processados da Petrobras 3W.
- Categoria: Eficiencia / Persistencia.
- Mapeamento: Milvus (`data/milvus/`), MinIO (`data/minio/`) e PostgreSQL (`data/postgres/`).

***RNF03*** **- Rastreabilidade e auditoria (MLOps)**
- Descricao: O sistema deve manter o tracking de versionamento dos modelos LLM (Ollama locais), prompts, parametros e metricas de experimentacao.
- Categoria: Rastreabilidade / Auditoria.
- Mapeamento: `infra/mlflow/` e `src/backend/app/mlflow_integration.py`.

***RNF04*** **- Monitoramento e desempenho**
- Descricao: O sistema deve ser monitorado continuamente, expondo metricas de uso de recursos, tempos de resposta de API e monitoramento de consumo de GPU.
- Categoria: Desempenho (Performance).
- Mapeamento: `infra/podman-compose/docker-compose.monitoring.yml` (Prometheus + Grafana + DCGM).

***RNF05*** - **Seguranca e privacidade**
- Descricao: O acesso a base de dados vetorial e bancos SQL pelos agentes especialistas deve ser estritamente mediado por regras de permissao (baseadas no cargo do usuario chamador do orquestrador).
- Categoria: Seguranca.
- Mapeamento: `src/backend/app/agents/orchestrator.py` validando contra o PostgreSQL.

## 📊 Impacto na modelagem e gestao agil do projeto

### Por que a EDA entra como requisito
A inclusao da EDA nao e apenas tecnica. Ela afeta o planejamento visual e agil do projeto porque estabelece a base para qualquer implementacao do RAG.

### Consequencias diretas no planejamento
- Fase de Analise na modelagem: seguindo diretrizes de Modelagem de Sistemas, essa etapa de exploracao de dados se encaixa na fase de Analise, cujo objetivo e a aquisicao de conhecimento sobre um sistema. Sem conhecer as particularidades do 3W, nao e possivel avançar com seguranca para a Implementação (codificacao da solucao do RAG).
- Gestao agil (Backlog e Kanban): a etapa investigativa deve compor o Backlog Priorizado e ser dividida em tarefas (cards) para as primeiras Sprints. E importante notar que o Lead Time do "Agente Especialista em Anomalias" comeca a ser contado a partir do inicio da EDA. O monitoramento agil no Kanban ajuda a controlar quanto tempo (Cycle Time) a equipe gasta limpando e entendendo os dados antes de codificar o agente.
