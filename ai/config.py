from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """Конфигурация AI-слоя. Значения берутся из .env или переменных окружения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # В .env лежат ещё и переменные FastAPI/Postgres
    )

    llm_provider: Literal["ollama", "qwen_api"] = "ollama"
    ollama_model: str = "qwen2.5-coder:7b"
    ollama_base_url: str = "http://localhost:11434"
    qwen_model: str = "qwen-plus"
    qwen_base_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_api_key: SecretStr | None = None
    llm_temperature: float = 0.1
    ai_repo_root: str | Path = "../app-conf-project-todo-list"
    ai_deny_globs: str = ".env*,*.pem,*.key,.git,secrets"
    ai_exclude_dirs: str = "git,.venv,venv,node_modules,__pycache__,dist,build,.pytest_cache,.ruff_cache,.chroma,tests"
    ai_tool_timeout_s: int = 30
        # поиск по документации (практика 3)
    ai_index_dir: str = "../.chroma"  # каталог индекса ChromaDB от корня помощника; в .gitignore
    ai_index_backend_globs: str = "README.md,CONTRIBUTING.md,docs/*.md,*.py"  # из *.py — только docstrings
    ai_index_assistant_globs: str = "README.md,docs/adr/*.md,docs/tools-spec-cycle2.md"
    ai_embed_model: str = "embeddinggemma"  # одна модель для индекса и для запроса
    ai_embed_query_prefix: str = ""  # префикс вопроса по карточке модели; пусто — без префикса
    ai_embed_doc_prefix: str = ""  # префикс чанка при индексации; пусто — без префикса
    ai_embed_timeout_s: int = 300  # ожидание ответа Ollama на одну порцию, секунды
    ai_search_top_k: int = 3  # сколько фрагментов по умолчанию; потолок 5 — в коде
    ai_search_max_distance: float = 2.0  # порог расстояния cosine; 2.0 — порога нет


settings = AISettings()