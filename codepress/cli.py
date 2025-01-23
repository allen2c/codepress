import logging
import pathlib
import typing

import click
from logging_bullet_train import set_logger

from codepress import LOGGER_NAME, walk_files

logger = logging.getLogger(__name__)
set_logger(LOGGER_NAME)


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
def main(
    path: typing.Text | pathlib.Path,
    ignore: typing.Iterable[typing.Text],
    ignore_hidden: bool,
    enable_gitignore: bool,
    truncate_lines: int,
):
    """
    Transforms code into clean, readable text with precision and style.

    PATH is the directory or file to process (default is current directory).
    """

    path = pathlib.Path(path)

    for file in walk_files(
        path,
        ignore_patterns=ignore,
        ignore_hidden=ignore_hidden,
        enable_gitignore=enable_gitignore,
        truncate_lines=truncate_lines,
    ):
        logger.info(file.path)


if __name__ == "__main__":
    main()
