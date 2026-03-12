import json
import os
import sys
from pathlib import Path

import pandas as pd
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

# Permite execucao direta do arquivo (python /app/rag/ingestao_3w.py) dentro do container.
APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

try:
    from rag.embeddings import gerar_embeddings_batch
except ModuleNotFoundError:
    from app.rag.embeddings import gerar_embeddings_batch


COLLECTION_NAME = "anomalias_3w"


def _resolver_caminho_parquet() -> Path:
    env_path = os.getenv("DATASET_3W_PARQUET")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
        raise FileNotFoundError(
            f"DATASET_3W_PARQUET foi definido, mas nao existe: {path}"
        )

    candidatos = [
        Path("data/3W/dataset/well_A/well_A.parquet"),
        Path("/app/data/3W/dataset/well_A/well_A.parquet"),
        Path("3W/dataset/well_A/well_A.parquet"),
    ]
    for candidato in candidatos:
        if candidato.exists():
            return candidato

    encontrados = sorted(Path(".").rglob("well_A.parquet"))
    if encontrados:
        return encontrados[0]

    raise FileNotFoundError(
        "Nao encontrei o dataset 3W. Defina DATASET_3W_PARQUET ou coloque well_A.parquet em um caminho esperado."
    )


def _dim_embedding_colecao(collection: Collection) -> int | None:
    for field in collection.schema.fields:
        if field.name == "embedding":
            dim = field.params.get("dim")
            return int(dim) if dim is not None else None
    return None


def _obter_ou_criar_colecao(embedding_dim: int) -> Collection:
    connections.connect(host="milvus", port="19530")
    if utility.has_collection(COLLECTION_NAME):
        collection = Collection(name=COLLECTION_NAME)
        dim_existente = _dim_embedding_colecao(collection)
        if dim_existente == embedding_dim:
            return collection

        if os.getenv("RECREATE_ON_DIM_MISMATCH", "1") == "1":
            utility.drop_collection(COLLECTION_NAME)
        else:
            raise ValueError(
                f"Colecao {COLLECTION_NAME} tem dim={dim_existente}, mas embedding atual tem dim={embedding_dim}."
            )

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="well", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="timestamp", dtype=DataType.VARCHAR, max_length=30),
        FieldSchema(name="sensor_data", dtype=DataType.VARCHAR, max_length=5000),
        FieldSchema(name="evento", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embedding_dim),
    ]
    schema = CollectionSchema(fields, description="Dados 3W")
    collection = Collection(name=COLLECTION_NAME, schema=schema)
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024},
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    return collection


def _normalizar_dataframe(df: pd.DataFrame, fonte: Path) -> pd.DataFrame:
    if "well" not in df.columns:
        df["well"] = fonte.stem
    if "timestamp" not in df.columns:
        df["timestamp"] = df.index.astype(str)
    if "evento" not in df.columns:
        if "class" in df.columns:
            df["evento"] = df["class"].astype(str)
        elif "state" in df.columns:
            df["evento"] = df["state"].astype(str)
        else:
            df["evento"] = "normal"
    return df


def main() -> None:
    parquet_path = _resolver_caminho_parquet()
    df = pd.read_parquet(parquet_path)
    max_rows_env = os.getenv("INGEST_MAX_ROWS")
    if max_rows_env:
        try:
            max_rows = int(max_rows_env)
            if max_rows > 0:
                df = df.head(max_rows)
        except ValueError:
            pass
    df = _normalizar_dataframe(df, parquet_path)

    sensor_cols = [c for c in df.columns if c not in ["well", "timestamp", "evento", "class", "state"]]
    textos = df.apply(
        lambda row: (
            f"Well {row['well']} at {row['timestamp']} sensors: "
            f"{row[sensor_cols].to_dict()}"
        ),
        axis=1,
    ).tolist()
    embeddings = gerar_embeddings_batch(textos)
    embedding_dim = len(embeddings[0]) if embeddings else 0
    if embedding_dim <= 0:
        raise ValueError("Nao foi possivel gerar embeddings para os registros selecionados.")
    collection = _obter_ou_criar_colecao(embedding_dim)
    sensor_data_list = [
        json.dumps(row, ensure_ascii=True) for row in df[sensor_cols].to_dict(orient="records")
    ]

    insert_data = [
        df["well"].astype(str).tolist(),
        df["timestamp"].astype(str).tolist(),
        sensor_data_list,
        df["evento"].fillna("normal").astype(str).tolist(),
        embeddings,
    ]
    collection.insert(insert_data)
    collection.flush()
    print(f"Inseridos {len(df)} registros de {parquet_path}")


if __name__ == "__main__":
    main()
