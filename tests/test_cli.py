"""Обязательные тесты курса: python -m ai <сценарий>. Без CrewAI и без Ollama."""

import sys
import types
from unittest import mock

import pytest

from ai.__main__ import SCENARIOS, main


@pytest.fixture
def fake_crew():
    """Подставной ai.run_crew: настоящий загрузил бы CrewAI."""
    module = types.ModuleType("ai.run_crew")
    module.main = mock.Mock(return_value=0)
    with mock.patch.dict(sys.modules, {"ai.run_crew": module}):
        yield module.main


def test_generate_tests_is_a_scenario():
    assert "generate-tests" in SCENARIOS


def test_task_is_passed_to_crew(fake_crew):
    assert main(["ai", "generate-tests", "Нужен тест: GET /version"]) == 0
    assert fake_crew.call_args.args[0][1] == "Нужен тест: GET /version"


def test_code_from_crew_is_returned(fake_crew):
    fake_crew.return_value = 1
    assert main(["ai", "generate-tests", "задача"]) == 1


@pytest.mark.parametrize("argv", [["ai"], ["ai", "no-such-scenario"]])
def test_call_error_prints_scenarios(argv, capsys):
    assert main(argv) == 2
    assert "generate-tests" in capsys.readouterr().out


@pytest.mark.parametrize("argv", [["ai", "generate-tests"], ["ai", "generate-tests", "  "]])
def test_task_is_required(argv, fake_crew):
    assert main(argv) == 2
    fake_crew.assert_not_called()