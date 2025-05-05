import io
import logging
import os
import pathlib
import textwrap
import typing

import jinja2
import pathspec
import puremagic

from codepress.version import VERSION

try:
    import tiktoken

    tiktoken_enc = tiktoken.encoding_for_model("gpt-4o")
except ImportError:
    tiktoken = None
    tiktoken_enc = None

__version__ = VERSION
LOGGER_NAME = "codepress"

logger = logging.getLogger(LOGGER_NAME)

DEFAULT_CONTENT_STYLE = textwrap.dedent(
    """
    # ==============================
    # File: {{ file.path }}

    {{ file.content }}

    # End of file
    # ==============================

    """
)


class FileWithContent:
    def __init__(self, path: pathlib.Path | typing.Text, content: typing.Text):
        self.path = pathlib.Path(path) if not isinstance(path, pathlib.Path) else path
        self.content = content

        self._total_tokens: int | None = None
        self._total_lines: int | None = None

    def __dict__(self) -> typing.Dict[typing.Text, typing.Text]:
        return {"path": str(self.path), "content": self.content}

    @property
    def total_lines(self) -> int:
        if self._total_lines is None:
            self._total_lines = self.content.count("\n") + 1
        return self._total_lines

    def get_total_tokens(self, *, inspect: bool = False) -> int:
        if self._total_tokens is None:
            if not inspect:
                self._total_tokens = 0
            elif tiktoken_enc is None:
                logger.warning(
                    "The 'tiktoken' package is not installed, token count will be 0"
                )
                self._total_tokens = 0
            else:
                self._total_tokens = len(tiktoken_enc.encode(self.content))
        return self._total_tokens

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


def is_text_file(file_path: pathlib.Path | typing.Text) -> bool:
    """
    Checks if the given file is likely a text file by:
    1. Reading a small chunk in binary mode to look for null bytes.
    2. Attempting to decode the chunk as UTF-8.
    """

    path = (
        pathlib.Path(file_path)
        if not isinstance(file_path, pathlib.Path)
        else file_path
    )

    # If it's a directory, it's not a text file
    if path.is_dir():
        return False

    try:
        # Get the MIME type of the file
        mime_type = puremagic.from_file(str(path), mime=True)
    except Exception as e:
        logger.debug(f"Can't determine the MIME type of {path}: {e}")
        # Fallback: perform a heuristic check
        try:
            with open(path, "rb") as f:
                chunk = f.read(1024)  # read the first 1KB
            # If null bytes are found, likely not a text file
            if b"\0" in chunk:
                return False
            # Try decoding the chunk as UTF-8 to verify it's text
            chunk.decode("utf-8")
            logger.debug(f"Consumed {path} as text")
            return True
        except Exception as fallback_e:
            logger.error(f"Fallback check failed for {path}: {fallback_e}")
            return False

    # Check if the MIME type indicates a text file
    if (
        mime_type.startswith("image/")
        or mime_type.startswith("video/")
        or mime_type.startswith("audio/")
        or mime_type.startswith("font/")
        or mime_type.startswith("model/")
    ):
        return False
    elif mime_type.startswith("application/"):
        binary_types = (
            "font-woff",
            "font-woff2",
            "gzip",
            "mathematica",
            "octet-stream",
            "pdf",
            "vnd.android.package-archive",
            "vnd.apple.installer+xml",
            "vnd.autodesk.dwg",
            "vnd.debian.binary-package",
            "vnd.dwf",
            "vnd.dxf",
            "vnd.google-earth.kml+xml",
            "vnd.google-earth.kmz",
            "vnd.ms-excel",
            "vnd.ms-fontobject",
            "vnd.ms-powerpoint",
            "vnd.oasis.opendocument.spreadsheet",
            "vnd.openxmlformats-officedocument.wordprocessingml.document",
            "vnd.wolfram.player",
            "x-7z-compressed",
            "x-apple-diskimage",
            "x-bzip2",
            "x-executable",
            "x-iso9660-image",
            "x-java-archive",
            "x-ms-wmz",
            "x-msdownload",
            "x-netcdf",
            "x-nintendo-3ds-rom",
            "x-pem-file",
            "x-pkcs12",
            "x-rar-compressed",
            "x-sharedlib",
            "x-shockwave-flash",
            "x-tar",
            "x-x509-ca-cert",
            "zip",
        )
        if any(mime_type.endswith(bt) for bt in binary_types):
            return False

    return True


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
    ignore_patterns: typing.Iterable[typing.Text] = (),
    *args,
    ignore_hidden: bool = True,
    enable_gitignore: bool = True,
    truncate_lines: bool | int = 5000,
    **kwargs,
) -> typing.Generator[FileWithContent, None, None]:
    path = pathlib.Path(path) if not isinstance(path, pathlib.Path) else path
    # Initialize a list to hold all pathspecs
    spec_list = []

    # Compile the initial ignore patterns using pathspec
    if ignore_patterns:
        spec_list.append(pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns))

    # If the path is a file, yield the file content
    if path.is_file():
        _is_text_file = is_text_file(path)
        if not _is_text_file:
            logger.info(f"Skipping non-text file: {path}")
            return

        _file_content = read_file(path, truncate_lines)
        yield FileWithContent(path, _file_content)
        return

    # Otherwise, walk the directory and yield the file contents
    for root, dirs, files in os.walk(path):

        current_dir = pathlib.Path(root)

        # Handle .gitignore files
        if enable_gitignore:
            gitignore_path = current_dir / ".gitignore"
            if gitignore_path.exists():
                try:
                    spec_list.append(
                        pathspec.PathSpec.from_lines(
                            "gitwildmatch", read_gitignore(gitignore_path)
                        )
                    )
                    logger.debug(f"Loaded .gitignore from {gitignore_path}")
                except Exception as e:
                    logger.error(f"Error reading .gitignore at {gitignore_path}: {e}")

        # Prepare the combined spec
        combined_spec = pathspec.PathSpec.from_lines("gitwildmatch", [])
        for spec in spec_list:
            combined_spec = combined_spec + spec

        # Filter directories in-place to respect ignore rules
        dirs[:] = [
            d
            for d in dirs
            if not (ignore_hidden and d.startswith("."))
            and not combined_spec.match_file((current_dir / d).relative_to(path))
        ]

        for file in files:

            # Ignore hidden files if `ignore_hidden` is True
            if ignore_hidden and file.startswith("."):
                continue

            _file_path = current_dir / file

            # Compute the relative path from the root path
            try:
                relative_path = _file_path.relative_to(path)
            except ValueError:
                # If _file_path is not relative to path, skip it
                logger.warning(f"Skipping {_file_path} as it's not relative to {path}")
                continue

            # Check against all ignore patterns
            if combined_spec.match_file(relative_path):
                logger.debug(f"Ignored by .gitignore: {relative_path}")
                continue

            _is_text_file = is_text_file(_file_path)
            if not _is_text_file:
                logger.info(f"Skipping non-text file: {_file_path}")
                continue

            try:
                _file_content = read_file(_file_path, truncate_lines)
            except Exception as e:
                logger.error(f"Error reading file {_file_path}: {e}")
                continue

            _file_content_obj = FileWithContent(_file_path, _file_content)

            yield _file_content_obj


if __name__ == "__main__":
    from logging_bullet_train import set_logger

    set_logger(logger)

    for file in walk_files(pathlib.Path(".")):
        logger.info(f"Read {file.path}")
