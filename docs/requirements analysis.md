## Requisitos

### 🧾 Baseline tecnico do Dataset 3W (levantamento local)
Este baseline consolida os dados reais observados no repositorio e deve orientar backlog, ingestao e criterios de aceite:

- Versao do dataset: `2.0.0` (`3W/dataset/dataset.ini`).
- Volume atual: `2228` arquivos Parquet, aproximadamente `1.8 GB`.
- Cobertura temporal observada em amostras: frequencia de `1 Hz` (passo de 1 segundo).
- Estrutura observada: schema unico com `30` colunas (`27` variaveis de processo + `class` + `state` + `timestamp`).
- Rotulos de evento principais: `0..9`.
- Rotulos transientes: `101..109` (offset `+100` conforme `TRANSIENT_OFFSET=100`).
- Linhas sem rotulo (`class/state = null`): presentes e relevantes em parte dos arquivos, exigindo tratamento explicito no pipeline.

### ⚙️ Requisitos Funcionais (RF)
Estes requisitos detalham o comportamento do sistema e se conectam diretamente com os diretórios `src/` e `data/`.

***RF01*** **- Interacao de usuario via chatbot**
- Descricao: O sistema deve prover uma interface conversacional web onde o colaborador possa enviar perguntas em linguagem natural.
- Mapeamento: `src/frontend/app.py` (Gradio).
- Classificacao: Essencial.

***RF02*** - **Orquestracao e controle de acesso**
- Descricao: O sistema deve receber a pergunta e decidir qual agente especialista 3W sera acionado (anomalias, qualidade de dados, desempenho operacional), com roteamento explicito e auditavel.
- Mapeamento: `src/backend/app/agents/orchestrator.py`.
- Classificacao: Essencial.

***RF03*** **- Consulta especializada em anomalias (Dataset 3W)**
- Descricao: O sistema deve possuir um agente especialista capaz de consultar, interpretar e responder perguntas sobre eventos indesejaveis em pocos de petroleo, considerando rotulos `0..9`, transientes `101..109` e periodos sem rotulo quando existirem.
- Mapeamento: `src/backend/app/agents/anomalias.py`.
- Classificacao: Essencial.

***RF04*** **- Consulta especializada em desempenho operacional de pocos**
- Descricao: O sistema deve possuir um agente especialista focado em desempenho operacional dos pocos do 3W, capaz de correlacionar variaveis de pressao, temperatura e vazao para explicar degradacao operacional e apoiar diagnostico.
- Mapeamento: `src/backend/app/agents/desempenho_operacional.py` (novo agente especialista orientado ao 3W).
- Classificacao: Importante.

***RF05*** **- Processamento RAG (Retrieval-Augmented Generation)**
- Descricao: O sistema deve fatiar documentos (chunking), gerar embeddings, buscar contexto relevante e injetar no prompt do LLM para a resposta final.
- Mapeamento: `src/backend/app/rag/` (`embeddings.py`, `retrieval.py`, `ingestao_3w.py`).
- Classificacao: Essencial.

***RF06*** **- Analise exploratoria (EDA) e pre-processamento de dados (Dataset 3W)**
- Descricao: O projeto deve contemplar a execucao de scripts e notebooks para a extracao, exploracao, identificacao de tipos de dados, limpeza e transformacao dos dados brutos do dataset 3W, incluindo validacoes de rotulos, para preparar o pipeline RAG e a ingestao vetorial.
- Visibilidade: Pode ser classificado como um requisito funcional oculto, visto que toda essa preparacao dos dados sera efetuada pela arquitetura do sistema sem o conhecimento explicito do colaborador que esta interagindo com o chat final.
- Mapeamento: `docs/eda_3w_dataset.ipynb` (exploracao), `src/backend/app/rag/ingestao_3w.py` (preparo para ingestao) e armazenamento persistente em `data/` (`data/milvus/`, `data/minio-milvus/`, `data/postgres/`).
- Classificacao (necessidade): Essencial. E um requisito imprescindivel sem o qual a consulta ao banco vetorial nao podera entrar em funcionamento.
- Prioridade: Alta (Essencial + Urgente), devendo ser uma das primeiras etapas praticas do cronograma.

***RF07*** **- Governanca de rotulos e qualidade de dados para o RAG**
- Descricao: O pipeline deve classificar explicitamente cada observacao entre `normal`, `evento`, `transiente` ou `sem rotulo`, com regras claras para ingestao (incluir, excluir ou marcar), preservando rastreabilidade por arquivo e classe.
- Mapeamento: `src/backend/app/rag/ingestao_3w.py`, `src/backend/app/rag/retrieval.py`, `docs/eda_3w_dataset.ipynb`.
- Classificacao: Essencial.

### 🛡️ Requisitos Nao Funcionais (RNF)
Estes requisitos impõem restricoes de arquitetura, seguranca e desempenho, relacionando-se profundamente com as tecnologias escolhidas e o diretorio `infra/`.

***RNF01*** **- Restricao de implementacao (Conteinerizacao)**
- Descricao: Todo o ambiente (backend, frontend, bancos e monitoramento) deve ser conteinerizado utilizando a tecnologia Podman (rootless) orquestrada localmente.
- Categoria: Implementacao / Restricoes de hardware e software.
- Mapeamento: `infra/podman-compose/` e Dockerfiles.

***RNF02*** **- Armazenamento e recuperacao eficiente (Persistencia)**
- Descricao: A camada de dados deve suportar busca vetorial de alta performance para o RAG e armazenamento em data lake (Bronze, Silver, Gold) para os dados brutos/processados da Petrobras 3W.
- Categoria: Eficiencia / Persistencia.
- Mapeamento: Milvus (`data/milvus/`), MinIO (`data/minio-milvus/`) e PostgreSQL (`data/postgres/`).

***RNF03*** **- Rastreabilidade e auditoria (MLOps)**
- Descricao: O sistema deve manter rastreabilidade de prompts, modelos e parametros usados por execucao. Quando MLOps dedicado (ex.: MLflow) nao estiver implantado, o minimo obrigatorio e log estruturado em arquivo/container.
- Categoria: Rastreabilidade / Auditoria.
- Mapeamento: `src/backend/app/`, logs de container e backlog de MLOps dedicado.

***RNF04*** **- Monitoramento e desempenho**
- Descricao: O sistema deve monitorar tempos de resposta da API, saude dos servicos e capacidade de ingestao. Stack completa de observabilidade (Prometheus/Grafana/DCGM) e evolucao futura de backlog.
- Categoria: Desempenho (Performance).
- Mapeamento: `infra/podman-compose/podman-compose.yml`, `infra/podman-compose/Makefile`, `docs/runbook_mvp_rag.md`.

***RNF05*** - **Seguranca e privacidade**
- Descricao: O acesso aos servicos e dados deve ser mediado pelo backend e pelo orquestrador, com separacao clara de responsabilidades entre agentes e sem expor credenciais no frontend.
- Categoria: Seguranca.
- Mapeamento: `src/backend/app/main.py`, `src/backend/app/agents/orchestrator.py`, `infra/podman-compose/podman-compose.yml`.

***RNF06*** - **Confiabilidade da ingestao e observabilidade de dados**
- Descricao: A ingestao deve publicar metricas minimas por execucao (arquivos lidos, linhas processadas, linhas sem rotulo, distribuicao de classes, falhas por arquivo) para permitir auditoria e reproducao.
- Categoria: Confiabilidade / Observabilidade.
- Mapeamento: `src/backend/app/rag/ingestao_3w.py`, `infra/podman-compose/Makefile`, `docs/runbook_mvp_rag.md`.

## 📊 Impacto na modelagem e gestao agil do projeto

### Por que a EDA entra como requisito
A inclusao da EDA nao e apenas tecnica. Ela afeta o planejamento visual e agil do projeto porque estabelece a base para qualquer implementacao do RAG.

### Consequencias diretas no planejamento
- Fase de Analise na modelagem: seguindo diretrizes de Modelagem de Sistemas, essa etapa de exploracao de dados se encaixa na fase de Analise, cujo objetivo e a aquisicao de conhecimento sobre um sistema. Sem conhecer as particularidades do 3W, nao e possivel avançar com seguranca para a Implementação (codificacao da solucao do RAG).
- Gestao agil (Backlog e Kanban): a etapa investigativa deve compor o Backlog Priorizado e ser dividida em tarefas (cards) para as primeiras Sprints. E importante notar que o Lead Time do "Agente Especialista em Anomalias" comeca a ser contado a partir do inicio da EDA. O monitoramento agil no Kanban ajuda a controlar quanto tempo (Cycle Time) a equipe gasta limpando e entendendo os dados antes de codificar o agente.

### 📌 Itens de backlog obrigatorios para manter coerencia entre docs
- Definir politica de tratamento para `class/state = null` antes da ingestao no Milvus.
- Definir estrategia para rotulos transientes (`101..109`) no retrieval e na resposta do agente.
- Registrar no runbook criterios de sucesso da ingestao (contagem por classe + total ingerido).
- Validar, a cada ciclo, alinhamento entre `docs/eda_3w_dataset.ipynb`, `docs/runbook_mvp_rag.md` e implementacao em `src/backend/app/rag/`.
