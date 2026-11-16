"""Обязательные тесты курса: запись в generated/ и второй корень run_linter.

Не меняйте их под свою архитектуру. Корень помощника подменён временным каталогом:
без CrewAI, без Ollama и без сети.
"""

import json
from unittest import mock

import pytest

import ai.tools.generated_files as gf
from ai.tools.code_tools import run_linter

GOOD_TEST = 'def test_ok():\n    assert 1 + 1 == 2\n'
BAD_TEST = 'import os\n\n\ndef test_ok():\n    assert 1 + 1 == 2\n'


@pytest.fixture
def assistant(tmp_path_factory):
    """Корень помощника — отдельный временный каталог рядом с тестовым бэкендом."""
    root = tmp_path_factory.mktemp("assistant")
    (root / "generated").mkdir()
    (root / "generated" / "conftest.py").write_text("# conftest курса\n", encoding="utf-8")
    (root / ".env").write_text("CLOUD_API_KEY=secret\n", encoding="utf-8")
    with mock.patch.object(gf, "ASSISTANT_ROOT", root):
        yield root


def test_write_creates_file_in_assistant(s, repo, assistant):
    answer = json.loads(gf.write_generated("generated/test_x.py", GOOD_TEST, s))
    assert answer["status"] == "ok"
    assert answer["path"] == "generated/test_x.py"
    assert (assistant / "generated" / "test_x.py").read_text(encoding="utf-8") == GOOD_TEST
    assert not list(repo.rglob("test_x.py"))


@pytest.mark.parametrize(
    "path",
    ["test_x.py", "ai/test_x.py", "generated/../ai/test_x.py", "../generated/test_x.py", "/tmp/test_x.py"],
)
def test_write_outside_generated_is_error(s, repo, assistant, path):
    answer = json.loads(gf.write_generated(path, GOOD_TEST, s))
    assert answer["status"] == "error"
    assert not list(assistant.rglob("test_x.py"))
    assert not list(repo.rglob("test_x.py"))


@pytest.mark.parametrize(
    "path", ["generated/conftest.py", "generated/x.py", "generated/test_x.txt", "generated/sub/test_x.py"]
)
def test_write_only_test_files(s, assistant, path):
    answer = json.loads(gf.write_generated(path, GOOD_TEST, s))
    assert answer["status"] == "error"
    assert (assistant / "generated" / "conftest.py").read_text(encoding="utf-8") == "# conftest курса\n"


def test_write_empty_content_is_error(s, assistant):
    answer = json.loads(gf.write_generated("generated/test_x.py", "  \n", s))
    assert answer["status"] == "error"
    assert not (assistant / "generated" / "test_x.py").exists()


def test_lint_generated_finds_issue(s, assistant):
    gf.write_generated("generated/test_x.py", BAD_TEST, s)
    answer = json.loads(run_linter("generated/test_x.py", s))
    assert answer["status"] == "ok"
    assert [(f["path"], f["rule"]) for f in answer["findings"]] == [("generated/test_x.py", "F401")]


def test_lint_generated_ignores_assistant_config(s, assistant):
    (assistant / "ruff.toml").write_text('[lint]\nignore = ["F401"]\n', encoding="utf-8")
    gf.write_generated("generated/test_x.py", BAD_TEST, s)
    answer = json.loads(run_linter("generated/test_x.py", s))
    assert [f["rule"] for f in answer["findings"]] == ["F401"]


def test_lint_generated_outside_is_error(s, assistant):
    (assistant / "ai").mkdir()
    (assistant / "ai" / "config.py").write_text("import os\n", encoding="utf-8")
    answer = json.loads(run_linter("generated/../ai/config.py", s))
    assert answer["status"] == "error"
    assert "generated/" in answer["message"]


def test_generated_prefix_means_assistant(s, repo, assistant):
    (repo / "generated").mkdir()
    (repo / "generated" / "test_backend.py").write_text("import os\n", encoding="utf-8")
    answer = json.loads(run_linter("generated/test_backend.py", s))
    assert answer["status"] == "error"
    assert "не найден" in answer["message"]


def test_lint_generated_writes_nothing(s, repo, assistant):
    gf.write_generated("generated/test_x.py", BAD_TEST, s)
    run_linter("generated/test_x.py", s)
    assert not (assistant / ".ruff_cache").exists()
    assert not (repo / ".ruff_cache").exists()
