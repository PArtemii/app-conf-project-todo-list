"""Тесты команды: пять атак из раздела «Тесты на практику 2»."""
import json
from ai.tools.code_tools import read_file, run_linter, search_codebase

def test_r3_loop_to_env(s):
    """Атака 1: Попытка выйти через .. в секретный файл .env"""
    answer = json.loads(read_file("../.env", s))
    assert answer["status"] == "error"
    assert "вне репозитория" in answer["message"]

def test_r6_binary_file(s, repo):
    """Атака 2: Чтение бинарного файла (картинки), который может сломать контекст"""
    (repo / "app" / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
    answer = json.loads(read_file("app/logo.png", s))
    assert answer["status"] == "error"

def test_s5_search_does_not_read_secrets(s):
    """Атака 3: Поиск секретов по кодовой базе"""
    answer = json.loads(search_codebase("API_KEY", s))
    assert answer["status"] == "ok"
    assert answer["total_matches"] == 0

def test_s2_too_general_query(s, repo):
    """Атака 4: Слишком общий запрос, возвращающий лавину данных"""
    (repo / "app" / "many.py").write_text("x = 1 # import\n" * 600, encoding="utf-8")
    answer = json.loads(search_codebase("import", s))
    assert answer["status"] == "ok"
    assert answer["total_matches"] > 500
    assert answer["matches"] == []
    assert "hint" in answer

def test_l4_flag_as_path(s):
    """Атака 5: Передача флага линтера вместо реального пути файла"""
    answer = json.loads(run_linter("--fix", s))
    assert answer["status"] == "error"
