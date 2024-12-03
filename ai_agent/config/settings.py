# LLM配置
LLM_CONFIG = {
    "temperature": 0.5,
    "model_name": "Qwen2.5-72B-Instruct",
    "openai_api_key": "xinference",
    "openai_api_base": "http://58.214.239.10:20008/v1",
    "streaming": True
}

# Embedding配置
EMBEDDING_CONFIG = {
    "MILVUS_HOST": "192.168.18.111",
    "MILVUS_PORT": "19531",
    "collection_name":"QA",
    "alias": "default",
    "BASE_URL": "http://192.168.18.111:20007",
    "EMBEDDING_MODEL_ID": "em",
    "RERANK_MODEL_ID": "re",
    "EMBEDDING_DIM": 768
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