import importlib
import json
import logging
import pathlib
import typing

import click
from logging_bullet_train import set_logger

from codepress import LOGGER_NAME, walk_files

logger = logging.getLogger(__name__)


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "--ignore",
    multiple=True,
    help="Patterns to ignore (can be specified multiple times)",
)
@click.option(
    "--ignore-hidden/--no-ignore-hidden",
    default=True,
    help="Ignore hidden files and directories",
)
@click.option(
    "--enable-gitignore/--no-enable-gitignore",
    default=True,
    help="Enable gitignore",
)
@click.option(
    "--truncate-lines",
    type=int,
    default=5000,
    help="Number of lines to read from each file (default: 5000)",
)
@click.option(
    "--output-format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format (default: text)",
)
@click.option(
    "--output-style",
    default="codepress:DEFAULT_CONTENT_STYLE",
    help="Output style (default: codepress:DEFAULT_CONTENT_STYLE). Skip style if output format is json.",  # noqa: E501
)
@click.option(
    "--output",
    default=None,
    type=click.Path(exists=False),
    help="Output file (default: stdout)",
)
@click.option(
    "--verbose/--no-verbose",
    default=False,
    help="Verbose output",
)
def main(
    path: typing.Text | pathlib.Path,
    ignore: typing.Iterable[typing.Text],
    ignore_hidden: bool,
    enable_gitignore: bool,
    truncate_lines: int,
    output_format: typing.Literal["text", "json"],
    output_style: typing.Text,
    output: typing.Text | pathlib.Path | None,
    verbose: bool,
):
    """
    Transforms code into clean, readable text with precision and style.

    PATH is the directory or file to process (default is current directory).
    """

    if verbose:
        set_logger(LOGGER_NAME)

    path = pathlib.Path(path)
    output = pathlib.Path(output) if output else None
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
    _style_module_name, _style_var_name = output_style.split(":")
    _style_module = importlib.import_module(_style_module_name)
    style = getattr(_style_module, _style_var_name)
    open_fs = open(output, "w") if output else None
    output_content_json: typing.List[typing.Dict[typing.Text, typing.Text]] = []

    # Walk files and process them
    try:
        for file in walk_files(
            path,
            ignore_patterns=ignore,
            ignore_hidden=ignore_hidden,
            enable_gitignore=enable_gitignore,
            truncate_lines=truncate_lines,
        ):
            if output_format == "text":
                if open_fs:
                    open_fs.write(file.to_content(style))
                else:
                    print(file.to_content(style))

            elif output_format == "json":
                output_content_json.append(file.__dict__())

        if output_format == "json":
            if open_fs:
                json.dump(output_content_json, open_fs, ensure_ascii=False, indent=2)
            else:
                print(json.dumps(output_content_json, ensure_ascii=False, indent=2))

    except Exception as e:
        logger.exception(e)
        logger.error(f"Error processing file: {file.path}")
        raise e

    finally:
        if open_fs:
            open_fs.close()


if __name__ == "__main__":
    main()
