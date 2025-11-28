import os
from pathlib import Path


def should_skip_dir(dirname: str) -> bool:
    skip_dirs = {".git", "__pycache__", ".venv", "env", "venv", ".idea", ".vscode"}
    return dirname in skip_dirs


def should_skip_file(path: Path, output_name: str, script_name: str) -> bool:
    # Пропускаем сам скрипт и файл с результатом
    if path.name in {output_name, script_name}:
        return True
    return False


def detect_language(path: Path) -> str:
    """Возвращает название языка для блока кода в Markdown по расширению файла."""
    mapping = {
        ".py": "python",
        ".json": "json",
        ".md": "markdown",
        ".txt": "text",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".ini": "ini",
        ".cfg": "ini",
    }
    return mapping.get(path.suffix.lower(), "")


def export_project_to_md(root: Path, output_filename: str = "project_dump.md") -> None:
    script_name = Path(__file__).name
    output_path = root / output_filename

    with output_path.open("w", encoding="utf-8") as out:
        out.write(f"# Project dump for `{root.name}`\n\n")

        for dirpath, dirnames, filenames in os.walk(root):
            # Фильтрация директорий на месте, чтобы os.walk не заходил внутрь
            dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

            for filename in sorted(filenames):
                file_path = Path(dirpath) / filename
                rel_path = file_path.relative_to(root)

                if should_skip_file(file_path, output_filename, script_name):
                    continue

                # Пропускаем бинарные/очевидно неподходящие файлы по расширению
                if file_path.suffix.lower() in {".pyc", ".pyo", ".pyd", ".so", ".dll", ".dylib", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".pdf", ".zip", ".tar", ".gz", ".xz"}:
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    # Если файл не читается как текст — пропускаем
                    continue

                lang = detect_language(file_path)

                out.write(f"## {rel_path}\n\n")
                if lang:
                    out.write(f"```{lang}\n")
                else:
                    out.write("```\n")

                out.write(content)

                # Гарантируем перевод строки перед закрывающими бэктиками
                if not content.endswith("\n"):
                    out.write("\n")

                out.write("```\n\n")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    export_project_to_md(project_root)
    print("project_dump.md успешно создан (или обновлен) в корне проекта.")
