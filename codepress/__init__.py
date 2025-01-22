import fnmatch
import io
import logging
import os
import pathlib
import textwrap
import typing

import jinja2

LOGGER_NAME = "codepress"

logger = logging.getLogger(LOGGER_NAME)

DEFAULT_CONTENT_STYLE = textwrap.dedent(
    """
    # ==============================
    # File: {{ file.path }}
    # ==============================

    {{ file.content }}

    # ==============================
    # End of file
    # ==============================

    """
)


class FileWithContent:
    def __init__(self, path: pathlib.Path | typing.Text, content: typing.Text):
        self.path = pathlib.Path(path) if not isinstance(path, pathlib.Path) else path
        self.content = content

    def __dict__(self) -> typing.Dict[typing.Text, typing.Text]:
        return {"path": str(self.path), "content": self.content}

    def to_content(self, style: typing.Text = DEFAULT_CONTENT_STYLE) -> typing.Text:
        return jinja2.Template(style).render(file=self)


def read_gitignore(file_path: pathlib.Path | typing.Text) -> typing.List[typing.Text]:
    """
    Reads the `.gitignore` file and returns a list of patterns, ignoring comments and blank lines.
    """  # noqa: E501

    file_path = (
        pathlib.Path(file_path)
        if not isinstance(file_path, pathlib.Path)
        else file_path
    )

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} does not exist.")

    patterns: typing.List[typing.Text] = []
    with file_path.open("r") as file:
        for line in file:
            line = line.strip()
            # Skip comments and blank lines
            if line and not line.startswith("#"):
                patterns.append(line)
    return patterns


def is_ignored(
    path: pathlib.Path | typing.Text, patterns: typing.List[typing.Text]
) -> bool:
    """
    Checks if the given path matches any of the `.gitignore` patterns.
    """

    path = pathlib.Path(path) if not isinstance(path, pathlib.Path) else path

    for pattern in patterns:
        if fnmatch.fnmatch(path.as_posix(), pattern):
            return True
    return False


def read_file(
    file_path: pathlib.Path | typing.Text, truncate_lines: bool | int | None = 5000
) -> typing.Text:
    if truncate_lines is True:
        truncate_lines = 5000
    elif truncate_lines is False:
        truncate_lines = None
    elif truncate_lines is not None and truncate_lines < 0:
        logger.error("Value of truncate_lines must be a positive integer or None")
        raise ValueError("Value of truncate_lines must be a positive integer or None")

    # If no truncation is needed, read everything at once
    if truncate_lines is None:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # Otherwise, read line-by-line up to the desired limit
    buffer = io.StringIO()
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= truncate_lines:
                break
            buffer.write(line)

    return buffer.getvalue()


def walk_files(
    path: pathlib.Path | typing.Text,
    ignore_patterns: typing.List[typing.Text],
    *args,
    ignore_hidden: bool = True,
    truncate_lines: bool | int = 5000,
    **kwargs,
) -> typing.Generator[FileWithContent, None, None]:
    for root, _, files in os.walk(path):
        for file in files:

            # Ignore files that match any of the ignore patterns
            if is_ignored(file, ignore_patterns):
                continue

            # Ignore hidden files and directories
            if ignore_hidden and (
                file.startswith(".")  # file name, e.g. .gitignore
                or any(
                    part.startswith(".") for part in pathlib.Path(root).parts
                )  # directory name, e.g. .tox
            ):
                continue

            _file_path = pathlib.Path(root).joinpath(file)
            file_content_obj = FileWithContent(
                _file_path, read_file(_file_path, truncate_lines)
            )

            yield file_content_obj


if __name__ == "__main__":
    from logging_bullet_train import set_logger

    set_logger(logger)

    for file in walk_files(
        pathlib.Path("."), ignore_patterns=read_gitignore(".gitignore")
    ):
        print(file.to_content())
