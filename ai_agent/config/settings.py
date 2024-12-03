import os
from typing import Dict

# LLM配置
LLM_CONFIG: Dict = {
    "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.5")),
    "model_name": os.environ.get("LLM_MODEL_NAME", "Qwen2.5-72B-Instruct"),
    "openai_api_key": os.environ.get("OPENAI_API_KEY", "xinference"),
    "openai_api_base": os.environ.get("OPENAI_API_BASE", "http://55.55.55.55:55/v1"),
    "streaming": os.environ.get("LLM_STREAMING", "True").lower() == "true"
}

# Embedding配置
EMBEDDING_CONFIG: Dict = {
    "MILVUS_HOST": os.environ.get("MILVUS_HOST", "192.168.18.111"),
    "MILVUS_PORT": os.environ.get("MILVUS_PORT", "19531"),
    "collection_name": os.environ.get("MILVUS_COLLECTION_NAME", "QA"),
    "alias": os.environ.get("MILVUS_ALIAS", "default"),
    "BASE_URL": os.environ.get("EMBEDDING_BASE_URL", "http://192.168.18.111:20007"),
    "EMBEDDING_MODEL_ID": os.environ.get("EMBEDDING_MODEL_ID", "em"),
    "RERANK_MODEL_ID": os.environ.get("RERANK_MODEL_ID", "re"),
    "EMBEDDING_DIM": int(os.environ.get("EMBEDDING_DIM", "768"))
}

# 文档处理配置
DOC_PROCESS_CONFIG = {
    "CHUNK_SIZE": 1000,
    "CHUNK_OVERLAP": 200,
    "TOP_K_RESULTS": 3
}

# Agent配置
AGENT_CONFIG = {
    "verbose": True,
    "handle_parsing_errors": True,
    "max_iterations": 3
}