import pathlib
import typing

VERSION: typing.Final[typing.Text] = (
    pathlib.Path(__file__).parent.joinpath("VERSION").read_text().strip()
)
