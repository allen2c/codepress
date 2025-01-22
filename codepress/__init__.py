import fnmatch
import pathlib
import typing


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


if __name__ == "__main__":
    print(read_gitignore(".gitignore"))
    print(is_ignored(pathlib.Path("."), read_gitignore(".gitignore")))
