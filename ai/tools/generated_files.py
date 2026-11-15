
"""Безопасная запись файлов, создаваемых агентом Developer."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath, PureWindowsPath

from ai.config import AISettings
from ai.tools.code_tools import check_path


def _ok(**fields) -> str:
    return json.dumps({"status": "ok", **fields}, ensure_ascii=False)


def _fail(message: str) -> str:
    return json.dumps(
        {"status": "error", "message": message},
        ensure_ascii=False,
    )


def write_generated(path: str, content: str, s: AISettings) -> str:
    """Создаёт новый UTF-8 файл только внутри generated/."""

    if not isinstance(path, str) or not path.strip() or "\x00" in path:
        return _fail("недопустимый путь")

    if not isinstance(content, str):
        return _fail("content должен быть строкой")

    # Абсолютные пути Windows и POSIX запрещены.
    if PureWindowsPath(path).anchor or PurePosixPath(path).is_absolute():
        return _fail("абсолютный путь запрещён")

    # Запрещаем обход через '..' и неоднозначные разделители.
    if "\\" in path or ".." in PurePosixPath(path).parts:
        return _fail("недопустимый относительный путь")

    parts = PurePosixPath(path).parts
    if len(parts) < 2 or parts[0] != "generated":
        return _fail("запись разрешена только в generated/")

    root = Path(s.ai_repo_root).resolve()
    generated_root = root / "generated"

    # Общая политика безопасности проекта.
    target, error = check_path(path, s)
    if error:
        return error

    # Защита от выхода через символические ссылки и junction.
    if not target.is_relative_to(generated_root):
        return _fail("путь выходит за пределы generated/")

    # Не перезаписываем существующие файлы.
    if target.exists() or target.is_symlink():
        return _fail("файл уже существует")

    try:
        target.parent.mkdir(parents=True, exist_ok=True)

        # Режим x запрещает перезапись существующего файла.
        with target.open("x", encoding="utf-8", newline="\n") as file:
            file.write(content)

    except FileExistsError:
        return _fail("файл уже существует")
    except OSError:
        return _fail("не удалось записать файл")

    return _ok(
        path=target.relative_to(root).as_posix(),
        bytes_written=len(content.encode("utf-8")),
    )


def crewai_tools(s: AISettings | None = None) -> list:
    """Инструмент записи для агента Developer."""
    from crewai.tools import tool

    s = s or AISettings()

    @tool("write_generated")
    def write_generated_tool(path: str, content: str) -> str:
        """Создаёт новый UTF-8 файл только внутри generated/.

        Args:
            path: относительный путь, начинающийся с generated/.
            content: полное текстовое содержимое файла.

        Returns:
            JSON со статусом ok или error.
        """
        return write_generated(path, content, s)

    return [write_generated_tool]
