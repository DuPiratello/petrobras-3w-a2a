import json
import os
import sys
from pathlib import Path

import pandas as pd #type: ignore
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility #type: ignore

# Permite execucao direta do arquivo (python /app/rag/ingestao_3w.py) dentro do container.
APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

try:
    from rag.embeddings import gerar_embeddings_batch
except ModuleNotFoundError:
    from app.rag.embeddings import gerar_embeddings_batch


COLLECTION_NAME = "anomalias_3w"


def _resolver_parquets() -> list[Path]:
    env_path = os.getenv("DATASET_3W_PARQUET")
    if env_path:
        path = Path(env_path)
        if path.is_dir():
            encontrados = sorted(path.rglob("*.parquet"))
            if encontrados:
                return encontrados
            raise FileNotFoundError(f"Nenhum .parquet encontrado em: {path}")
        if path.exists():
            return [path]
        raise FileNotFoundError(
            f"DATASET_3W_PARQUET foi definido, mas nao existe: {path}"
        )

    env_glob = os.getenv("DATASET_3W_GLOB")
    if env_glob:
        encontrados = sorted(Path(".").glob(env_glob))
        if encontrados:
            return encontrados
        raise FileNotFoundError(f"Nenhum .parquet encontrado para glob: {env_glob}")

    candidatos = [
        Path("3W/dataset"),
        Path("/app/3W/dataset"),
        Path("data/3W/dataset"),
        Path("/app/data/3W/dataset"),
    ]
    for candidato in candidatos:
        if candidato.exists() and candidato.is_dir():
            encontrados = sorted(candidato.rglob("*.parquet"))
            if encontrados:
                return encontrados

    encontrados = sorted(Path(".").rglob("*.parquet"))
    if encontrados:
        return encontrados

    raise FileNotFoundError(
        "Nao encontrei .parquet do dataset 3W. Defina DATASET_3W_PARQUET ou DATASET_3W_GLOB."
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


def _ler_dataframe_limitado(parquet_path: Path) -> pd.DataFrame:
    df = pd.read_parquet(parquet_path)
    max_rows_env = os.getenv("INGEST_MAX_ROWS")
    if max_rows_env:
        try:
            max_rows = int(max_rows_env)
            if max_rows > 0:
                df = df.head(max_rows)
        except ValueError:
            pass
    return df


def main() -> None:
    parquets = _resolver_parquets()
    max_files_env = os.getenv("INGEST_MAX_FILES")
    if max_files_env:
        try:
            max_files = int(max_files_env)
            if max_files > 0:
                parquets = parquets[:max_files]
        except ValueError:
            pass

    if not parquets:
        raise FileNotFoundError("Nenhum arquivo .parquet encontrado para ingestao.")

    collection: Collection | None = None
    total_inseridos = 0
    for idx, parquet_path in enumerate(parquets, start=1):
        df = _ler_dataframe_limitado(parquet_path)
        if df.empty:
            print(f"[{idx}/{len(parquets)}] Ignorando vazio: {parquet_path}")
            continue
        df = _normalizar_dataframe(df, parquet_path)

        sensor_cols = [
            c for c in df.columns if c not in ["well", "timestamp", "evento", "class", "state"]
        ]
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
        if collection is None:
            collection = _obter_ou_criar_colecao(embedding_dim)

        sensor_data_list = [
            json.dumps(row, ensure_ascii=True)
            for row in df[sensor_cols].to_dict(orient="records")
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
        total_inseridos += len(df)
        print(f"[{idx}/{len(parquets)}] Inseridos {len(df)} registros de {parquet_path}")

    print(f"Ingestao concluida. Total de registros: {total_inseridos}")


if __name__ == "__main__":
    main()
