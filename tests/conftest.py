import os
import tempfile

# До импорта ai.config: модульный settings = AISettings() требует AI_REPO_ROOT,
# а в CI и на свежем клоне .env нет. Внутри pytest модульный settings поэтому
# смотрит во временный каталог (переменная окружения важнее .env); тесты
# инструментов передают свой корень явно.
os.environ.setdefault("AI_REPO_ROOT", tempfile.gettempdir())

import pytest

from ai.config import AISettings


@pytest.fixture
def repo(tmp_path):
    """Мини-репозиторий бэкенда во временном каталоге: код, нарушение ruff, секреты."""
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "main.py").write_text(
        "def health_check():\n"
        '    return {"status": "healthy"}\n'
        "\n"
        "\n"
        "class NoteIn:\n"
        '    title: str = ""\n',
        encoding="utf-8",
    )
    (tmp_path / "app" / "bad.py").write_text("import os\n", encoding="utf-8")
    (tmp_path / ".env").write_text("API_KEY=secret-from-env\n", encoding="utf-8")
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets" / "leak.py").write_text(
        "import os\nAPI_KEY = 'secret-from-secrets'\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def s(repo):
    """Настройки помощника с корнем в мини-репозитории; .env не читается."""
    return AISettings(ai_repo_root=repo, _env_file=None)