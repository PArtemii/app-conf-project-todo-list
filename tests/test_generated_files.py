
import json

import pytest

from ai.config import AISettings
from ai.tools.generated_files import write_generated


@pytest.fixture
def repo(tmp_path):
    """Создаёт временный репозиторий для каждого теста."""
    (tmp_path / "generated").mkdir()
    return tmp_path


@pytest.fixture
def settings(repo):
    """Настройки с изолированным тестовым репозиторием."""
    return AISettings(ai_repo_root=repo, _env_file=None)


def test_write_python_file(repo, settings):
    """Разрешена запись Python-файла в generated/."""
    result = json.loads(
        write_generated("generated/test_example.py", "def test_ok():\n    assert True\n", settings)
    )

    assert result["status"] == "ok"
    assert (repo / "generated" / "test_example.py").read_text(encoding="utf-8") == (
        "def test_ok():\n    assert True\n"
    )


def test_write_nested_file(repo, settings):
    """Разрешена запись в подкаталог generated/."""
    result = json.loads(
        write_generated("generated/unit/test_tasks.py", "def test_tasks():\n    pass\n", settings)
    )

    assert result["status"] == "ok"
    assert (repo / "generated" / "unit" / "test_tasks.py").exists()


@pytest.mark.parametrize(
    "path",
    [
        ".env",
        "app/main.py",
        "tests/test_existing.py",
        "../outside.py",
        "generated/../../outside.py",
        "/tmp/absolute.py",
        r"C:\Windows\test.py",
    ],
)
def test_write_outside_generated_is_denied(repo, settings, path):
    """Запись за пределами generated/ запрещена."""
    result = json.loads(write_generated(path, "print('unsafe')", settings))

    assert result["status"] == "error"


def test_existing_file_is_not_overwritten(repo, settings):
    """Существующий файл не должен перезаписываться без разрешения."""
    target = repo / "generated" / "test_existing.py"
    target.write_text("original\n", encoding="utf-8")

    result = json.loads(
        write_generated("generated/test_existing.py", "changed\n", settings)
    )

    assert result["status"] == "error"
    assert target.read_text(encoding="utf-8") == "original\n"


def test_symlink_escape_is_denied(repo, settings, tmp_path):
    """Символическая ссылка не должна позволять выйти за generated/."""
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    link = repo / "generated" / "external"

    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Создание символических ссылок недоступно")

    result = json.loads(
        write_generated("generated/external/test_escape.py", "unsafe\n", settings)
    )

    assert result["status"] == "error"
    assert not (outside / "test_escape.py").exists()


def test_empty_content_is_allowed(repo, settings):
    """Создание пустого файла разрешено."""
    result = json.loads(write_generated("generated/empty.py", "", settings))

    assert result["status"] == "ok"
    assert (repo / "generated" / "empty.py").exists()
