"""Обязательные тесты курса: граница корня, deny-list, коды ruff 0/1/2, чья конфигурация ruff.

Не меняйте их под свою v2: они вызывают только check_path и run_linter.
"""

import json
import sys

import pytest

from ai.config import AISettings
from ai.tools.code_tools import check_path, run_linter


def test_tests_do_not_import_crewai():
    assert "crewai" not in sys.modules


def test_outside_root(s):
    _, err = check_path("../outside.txt", s)
    assert "вне репозитория" in json.loads(err)["message"]


def test_absolute_path(s, repo):
    _, err = check_path(str(repo / "app" / "main.py"), s)
    assert "вне репозитория" in json.loads(err)["message"]


@pytest.mark.parametrize(
    "path", [".env", "app/../.env", "secrets/leak.py", "SECRETS/leak.py", ".git/config"]
)
def test_deny_list(s, path):
    _, err = check_path(path, s)
    assert err is not None
    assert "запрещён" in json.loads(err)["message"]


def test_allowed_path(s, repo):
    target, err = check_path("app/main.py", s)
    assert err is None
    assert target == (repo / "app" / "main.py").resolve()


def test_ruff_exit_0_ok_without_findings(s):
    answer = json.loads(run_linter("app/main.py", s))
    assert answer["status"] == "ok"
    assert answer["total_findings"] == 0


def test_ruff_exit_1_ok_with_findings(s):
    answer = json.loads(run_linter("app/bad.py", s))
    assert answer["status"] == "ok"
    assert answer["total_findings"] >= 1
    assert answer["findings"][0]["path"] == "app/bad.py"
    assert answer["findings"][0]["rule"] == "F401"


def test_ruff_exit_2_is_error(s, repo):
    (repo / "ruff.toml").write_text('line-length = "long"\n', encoding="utf-8")
    answer = json.loads(run_linter("app/main.py", s))
    assert answer["status"] == "error"
    assert "аварийно" in answer["message"]


def test_linter_ignores_config_outside_backend(tmp_path):
    (tmp_path / "ruff.toml").write_text('[lint]\nignore = ["F401"]\n', encoding="utf-8")
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "bad.py").write_text("import os\n", encoding="utf-8")
    answer = json.loads(run_linter("bad.py", AISettings(ai_repo_root=backend, _env_file=None)))
    assert [f["rule"] for f in answer["findings"]] == ["F401"]


def test_linter_missing_path(s):
    answer = json.loads(run_linter("app/no_such.py", s))
    assert answer["status"] == "error"


def test_linter_skips_denied_and_writes_nothing(s, repo):
    answer = json.loads(run_linter(".", s))
    assert answer["status"] == "ok"
    assert all(not (f["path"] or "").startswith("secrets/") for f in answer["findings"])
    assert not (repo / ".ruff_cache").exists()