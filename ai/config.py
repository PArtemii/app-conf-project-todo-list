from typing import Literal
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


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
    ai_exclude_dirs: str = ".git,.venv,venv,node_modules,__pycache__,dist,build"
    ai_tool_timeout_s: int = 30



settings = AISettings()