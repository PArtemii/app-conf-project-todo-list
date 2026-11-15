"""Обязательные тесты курса для поиска по документации: корпус, search_docs, docstrings.

Не меняйте их под свою схему. Эмбеддинги фальшивые, хранилище — ChromaDB в памяти:
без Ollama, без сети и без CrewAI.
"""

import json
import re
import zlib
from unittest import mock

import chromadb
import httpx
import pytest
from chromadb.config import Settings

import ai.tools.rag_pipeline as rp
from ai.config import AISettings

MARKER = "marker-test-secret"


def fake_embed(texts, s, kind="document"):
    """Детерминированный «эмбеддинг»: мешок слов в 64 ячейках. Общие слова — близкие векторы."""
    vectors = []
    for text in texts:
        v = [0.0] * 64
        for word in re.findall(r"\w+", text.lower()):
            v[zlib.crc32(word.encode()) % 64] += 1.0
        vectors.append(v if any(v) else [1.0] + [0.0] * 63)
    return vectors


@pytest.fixture
def backend(tmp_path):
    """Бэкенд: документы, docstring, а также секреты и мусор, которых не должно быть в индексе."""
    root = tmp_path / "backend"
    (root / "docs" / "adr").mkdir(parents=True)
    (root / "docs" / "secrets").mkdir()
    (root / ".venv" / "lib").mkdir(parents=True)
    sections = "\n\n".join(f"## Раздел {n}\n\nПравило номер {n} про ветки и коммиты." for n in range(1, 8))
    (root / "README.md").write_text(f"# Заметки\n\nУчебный бэкенд.\n\n{sections}\n", encoding="utf-8")
    (root / "docs" / "adr" / "001-storage.md").write_text(
        "# ADR 001\n\n## Решение\n\nЗаметки хранятся в памяти процесса.\n", encoding="utf-8"
    )
    (root / "main.py").write_text(
        'def health_check():\n    """Проверка, что сервис жив."""\n    return {"status": "healthy"}\n',
        encoding="utf-8",
    )
    (root / ".env").write_text(f"POSTGRES_PASSWORD={MARKER}\n", encoding="utf-8")
    (root / "docs" / "secrets" / "x.md").write_text(f"# Пароль\n\n{MARKER}\n", encoding="utf-8")
    (root / "compose.yaml").write_text(f"password: {MARKER}\n", encoding="utf-8")
    (root / ".venv" / "lib" / "README.md").write_text(f"# Пакет\n\n{MARKER}\n", encoding="utf-8")
    return root


@pytest.fixture
def assistant(tmp_path):
    """Помощник: свои документы, свой .env с ключом, кеш pytest и сам индекс."""
    root = tmp_path / "assistant"
    (root / "docs" / "adr").mkdir(parents=True)
    (root / ".pytest_cache").mkdir()
    (root / ".chroma").mkdir()
    (root / "README.md").write_text("# Помощник\n\n## Инструменты\n\nread_file и search_codebase.\n", encoding="utf-8")
    (root / "docs" / "adr" / "001-framework.md").write_text("# ADR 001\n\nВыбран CrewAI.\n", encoding="utf-8")
    (root / ".env").write_text(f"CLOUD_API_KEY={MARKER}\n", encoding="utf-8")
    (root / ".pytest_cache" / "README.md").write_text(f"# pytest cache\n\n{MARKER}\n", encoding="utf-8")
    (root / ".chroma" / "notes.md").write_text(f"# Индекс\n\n{MARKER}\n", encoding="utf-8")
    return root


@pytest.fixture
def rs(backend, tmp_path):
    """Настройки поиска: корень — тестовый бэкенд, индекс — во временном каталоге, .env не читается."""
    return AISettings(ai_repo_root=backend, ai_index_dir=str(tmp_path / "index"), _env_file=None)


@pytest.fixture
def client():
    """ChromaDB в памяти. Клиенты в памяти в одном процессе общие — перед тестом чистим."""
    c = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
    for col in c.list_collections():
        c.delete_collection(col.name)
    return c


@pytest.fixture
def index(rs, assistant, client):
    """Индекс построен на фальшивых эмбеддингах; _client подменён на клиент в памяти."""
    with mock.patch.object(rp, "_client", return_value=client):
        with mock.patch.object(rp, "embed", fake_embed):
            rp.build_index(rs, assistant_root=assistant, log=lambda *a: None)
        yield client


def search(rs, query, **kwargs):
    with mock.patch.object(rp, "embed", fake_embed):
        return json.loads(rp.search_docs(query, rs, **kwargs))


def test_backend_denied_and_excluded_not_collected(rs, assistant):
    everything = rs.model_copy(update={"ai_index_backend_globs": "*"})
    paths = {rel for source, rel, _ in rp.collect_files(everything, assistant) if source == "backend"}
    assert "README.md" in paths
    assert not paths & {".env", "docs/secrets/x.md", ".venv/lib/README.md"}


def test_assistant_denied_and_excluded_not_collected(rs, assistant):
    everything = rs.model_copy(update={"ai_index_assistant_globs": "*"})
    paths = {rel for source, rel, _ in rp.collect_files(everything, assistant) if source == "assistant"}
    assert "README.md" in paths
    assert not paths & {".env", ".pytest_cache/README.md", ".chroma/notes.md"}


def test_allow_list_default(rs, assistant):
    files = {(source, rel) for source, rel, _ in rp.collect_files(rs, assistant)}
    assert ("backend", "README.md") in files
    assert ("backend", "docs/adr/001-storage.md") in files
    assert ("backend", "main.py") in files
    assert ("assistant", "docs/adr/001-framework.md") in files
    assert ("backend", "compose.yaml") not in files


def test_marker_not_in_index(index):
    documents = index.get_collection(rp.COLLECTION).get()["documents"]
    assert documents
    assert all(MARKER not in doc for doc in documents)


def test_top_k_ceiling(rs, index):
    answer = search(rs, "правило про ветки и коммиты", top_k=100)
    assert answer["status"] == "ok"
    assert answer["returned"] <= rp.TOP_K_LIMIT
    assert answer["truncated"] is True


def test_matches_have_source(rs, index):
    answer = search(rs, "где хранятся заметки")
    assert answer["matches"]
    for match in answer["matches"]:
        assert match["source"] in ("backend", "assistant")
        assert match["path"]
        assert match["heading"]
        assert "text" in match and "distance" in match


def test_docstring_is_separate_chunk(rs, index):
    answer = search(rs, "Проверка, что сервис жив")
    top = answer["matches"][0]
    assert top["source"] == "backend"
    assert top["path"] == "main.py"
    assert top["symbol"] == "health_check"


def test_nothing_close_is_ok_with_hint(rs, index):
    strict = rs.model_copy(update={"ai_search_max_distance": 0.01})
    answer = search(strict, "рецепт борща со сметаной")
    assert answer["status"] == "ok"
    assert answer["matches"] == []
    assert "hint" in answer


def test_index_not_built(rs, client):
    with mock.patch.object(rp, "_client", return_value=client):
        answer = search(rs, "как называть ветки")
    assert answer["status"] == "error"
    assert "не построен" in answer["message"]


def test_index_dir_missing(rs):
    answer = search(rs, "как называть ветки")
    assert answer["status"] == "error"
    assert "не построен" in answer["message"]


def test_embeddings_unavailable_is_error(rs, index):
    with mock.patch.object(rp.httpx, "post", side_effect=httpx.ConnectError("connection refused")):
        answer = json.loads(rp.search_docs("как называть ветки", rs))
    assert answer["status"] == "error"
    assert "недоступна" in answer["message"]


def test_other_embedding_model_is_error(rs, index):
    other = rs.model_copy(update={"ai_embed_model": "qwen3-embedding:0.6b"})
    answer = search(other, "как называть ветки")
    assert answer["status"] == "error"
    assert "перестроить" in answer["hint"]


def test_partial_index_is_error(rs, assistant, client):
    calls = []

    def embed_then_fail(texts, s, kind="document"):
        calls.append(len(texts))
        if len(calls) > 1:
            raise rp.EmbedError("Ollama не ответила за 300 с")
        return fake_embed(texts, s, kind)

    with mock.patch.object(rp, "_client", return_value=client), mock.patch.object(rp, "EMBED_BATCH", 2):
        with mock.patch.object(rp, "embed", embed_then_fail), pytest.raises(rp.EmbedError):
            rp.build_index(rs, assistant_root=assistant, log=lambda *a: None)
        answer = search(rs, "как называть ветки")
    assert answer["status"] == "error"
    assert "не полностью" in answer["message"]



# --- тесты команды: правила из docs/rag-design.md ---

def test_team_secret_in_allowed_file(rs, assistant, client, backend):
    """Тест команды (Раздел 1): Проверка фильтрации секретов внутри текста."""
    # Создаем файл, который разрешен allow-list, но внутри него зашит пароль
    (backend / "docs" / "setup.md").write_text(
        "# Настройка\n\n Пароль базы: POSTGRES_PASSWORD=team-secret-42\n", 
        encoding="utf-8"
    )
with (
    mock.patch.object(rp, "_client", return_value=client),
    mock.patch.object(rp, "embed", fake_embed),
):
    rp.build_index(rs, assistant_root=assistant, log=lambda *a: None)
    # Достаем все документы из базы знаний и проверяем, что секретного пароля там НЕТ
    documents = client.get_collection(rp.COLLECTION).get()["documents"]
    assert documents
    assert all("team-secret-42" not in doc for doc in documents)

def test_team_table_not_split():
    """Тест команды (Раздел 2): Таблицы эндпоинтов не режутся посередине."""
    # Генерируем длинную таблицу эндпоинтов на 60 строк
    rows = "\n". join(f"| {n} | эндпоинт To-Do приложения {n} |" for n in range(60))
    table_text = f"# Чек-лист API\n\n| # | Описание |\n|---|---|\n{rows}\n"
    # Запускаем функцию нарезки и проверяем, что таблица ушла ОДНИМ монолитным чанком
    chunks = rp.split_markdown(table_text)
    assert len(chunks) == 1
