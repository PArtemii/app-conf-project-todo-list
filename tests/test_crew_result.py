"""Обязательные тесты курса: минимум контракта итога и проверки кодом.

Не меняйте их под свою архитектуру. Кто ловит нарушение, решает ваш столбец
«Что при нарушении»: rejected() принимает и отказ формата, и отказ кода.
"""

import os
import time
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from ai.crew_result import CrewResult, check_result, run_and_check

SCHEMA = {"paths": {"/version": {"get": {}}, "/notes/{note_id}": {"delete": {}}}}
TEST_FILE = "generated/test_version.py"


def good_case(**changes):
    case = {
        "name": "test_version_returns_200",
        "method": "GET",
        "path": "/version",
        "expected_status": 200,
        "expected_fields": [{"field": "team", "value": "repair-requests"}],
        "source": "main.py:47-50",
    }
    return case | changes


def good_data(**changes):
    data = {
        "search_status": "found",
        "test_file": TEST_FILE,
        "test_cases": [good_case()],
        "linter_result": "замечаний нет",
        "note": "Проверяет статус и поля ответа GET /version.",
    }
    return data | changes


@pytest.fixture
def root(tmp_path):
    """Корень помощника: файл теста записан только что."""
    (tmp_path / "generated").mkdir()
    (tmp_path / "generated" / "test_version.py").write_text("def test_x():\n    pass\n", encoding="utf-8")
    return tmp_path


STARTED = time.time() - 60  # запуск начался минуту назад


def problems_of(data, root):
    return check_result(CrewResult.model_validate(data), SCHEMA, STARTED, root)


def rejected(data, root):
    """True, если итог отверг формат или проверка кодом."""
    try:
        result = CrewResult.model_validate(data)
    except ValidationError:
        return True
    return bool(check_result(result, SCHEMA, STARTED, root))


def test_good_result_has_no_problems(root):
    assert problems_of(good_data(), root) == []


def no_test_data(status="not_found", test_file=""):
    return good_data(search_status=status, test_file=test_file, test_cases=[], note="Эндпоинта нет.")


def make_old(root):
    """Файл остался от прошлого запуска: изменён раньше начала этого."""
    old = STARTED - 3600
    os.utime(root / TEST_FILE, (old, old))


@pytest.mark.parametrize("status", ["not_found", "tool_error"])
def test_empty_result_when_no_test_is_valid(root, status):
    make_old(root)
    assert problems_of(no_test_data(status), root) == []


@pytest.mark.parametrize("field", ["search_status", "test_file", "test_cases", "linter_result", "note"])
def test_result_fields_are_required(field):
    data = good_data()
    del data[field]
    with pytest.raises(ValidationError):
        CrewResult.model_validate(data)


@pytest.mark.parametrize("field", ["name", "method", "path", "expected_status", "expected_fields", "source"])
def test_case_fields_are_required(field):
    case = good_case()
    del case[field]
    with pytest.raises(ValidationError):
        CrewResult.model_validate(good_data(test_cases=[case]))


@pytest.mark.parametrize(
    "bad",
    [
        {"search_status": "найдено"},
        {"test_cases": [good_case(method="FETCH")]},
        {"test_cases": [good_case(expected_status="двести")]},
        {"test_cases": [good_case(expected_fields="team")]},
    ],
)
def test_types_and_literals_rejected_by_format(bad):
    with pytest.raises(ValidationError):
        CrewResult.model_validate(good_data(**bad))


def test_status_as_number_string_is_converted():
    result = CrewResult.model_validate(good_data(test_cases=[good_case(expected_status="200")]))
    assert result.test_cases[0].expected_status == 200


@pytest.mark.parametrize(
    "bad",
    [
        {"test_file": "def test_x():\n    assert 1 == 1\n"},
        {"test_file": "generated/test_absent.py"},
        {"test_cases": [good_case(path="version")]},
        {"test_cases": [good_case(path="/versions")]},
        {"test_cases": [good_case(method="POST")]},
        {"test_cases": [good_case(path="/notes/999", method="DELETE")]},
        {"test_cases": []},
        {"test_file": ""},
    ],
)
def test_violations_are_rejected_at_any_level(root, bad):
    assert rejected(good_data(**bad), root)


def test_old_file_is_not_a_result(root):
    make_old(root)
    assert any("не записан" in problem for problem in problems_of(good_data(), root))


@pytest.mark.parametrize("status", ["not_found", "tool_error"])
@pytest.mark.parametrize("test_file", ["", TEST_FILE], ids=["test_file_empty", "test_file_filled"])
def test_fresh_file_without_found_is_rejected(root, status, test_file):
    problems = problems_of(no_test_data(status, test_file), root)
    assert any(status in problem and "записан в этом запуске" in problem for problem in problems)


def test_fresh_file_with_found_is_not_rejected(root):
    assert not any("search_status" in problem for problem in problems_of(good_data(), root))


class ConverterFailure(Exception):
    """Вместо ConverterError из CrewAI: тесты не загружают CrewAI."""


def kickoff_writing(data, root):
    """Как настоящий запуск: файл записан после начала запуска (время — с запасом)."""

    def kickoff():
        later = time.time() + 5
        os.utime(root / TEST_FILE, (later, later))
        return SimpleNamespace(pydantic=CrewResult.model_validate(data), raw="сырой текст")

    return kickoff


def kickoff_raising(error):
    def kickoff():
        raise error

    return kickoff


def validation_error():
    try:
        CrewResult.model_validate({})
    except ValidationError as exc:
        return exc


def test_run_good_result_returns_0(root, capsys):
    assert run_and_check(kickoff_writing(good_data(), root), SCHEMA, root=root) == 0
    out = capsys.readouterr().out
    assert "test_version_returns_200" in out
    assert "Отказ" not in out


def test_run_code_refusal_returns_1(root, capsys):
    data = good_data(test_cases=[good_case(path="/versions")])
    assert run_and_check(kickoff_writing(data, root), SCHEMA, root=root) == 1
    out = capsys.readouterr().out
    assert "Отказ кода" in out
    assert "Файл в generated/" in out


def test_run_fresh_file_without_found_returns_1(root, capsys):
    assert run_and_check(kickoff_writing(no_test_data(), root), SCHEMA, root=root) == 1
    out = capsys.readouterr().out
    assert "Отказ кода: search_status not_found" in out
    assert "Файл в generated/" in out
    assert "Traceback" not in out


def test_run_old_file_without_found_returns_0(root, capsys):
    make_old(root)
    result = SimpleNamespace(pydantic=CrewResult.model_validate(no_test_data()), raw="сырой текст")
    assert run_and_check(lambda: result, SCHEMA, root=root) == 0
    assert "Отказ" not in capsys.readouterr().out


@pytest.mark.parametrize(
    "error",
    [validation_error(), ConverterFailure("конвертер не справился"), TimeoutError(), RuntimeError("Task execution failed")],
    ids=["validation", "converter", "timeout", "llm"],
)
def test_run_exceptions_become_message(root, capsys, error):
    code = run_and_check(kickoff_raising(error), SCHEMA, root=root, converter_errors=(ConverterFailure,))
    assert code == 1
    out = capsys.readouterr().out
    assert "Файл в generated/" in out
    assert "Traceback" not in out


def test_run_without_object_is_refusal(root, capsys):
    result = SimpleNamespace(pydantic=None, raw="Тест записан.")
    assert run_and_check(lambda: result, SCHEMA, root=root) == 1
    assert "Отказ формата" in capsys.readouterr().out