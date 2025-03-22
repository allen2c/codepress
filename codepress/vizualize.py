import math
import pathlib


def get_token_color(tokens: int) -> str:
    """Get ANSI color code for token range."""
    if tokens < 5000:
        return "\033[42m"  # Green background
    elif tokens < 10000:
        return "\033[46m"  # Cyan background
    elif tokens < 50000:
        return "\033[43m"  # Yellow background
    elif tokens < 100000:
        return "\033[45m"  # Magenta background
    else:
        return "\033[41m"  # Red background


def format_bar_with_path(
    tokens: int, max_tokens: int, path: pathlib.Path, max_width: int = 60
) -> str:
    """Format a colored bar with the path text displayed on it, left-aligned."""

    # Get background color and reset code
    bg_color = get_token_color(tokens)
    reset = "\033[0m"

    # Convert path to string
    path_str = str(path)

    # Calculate bar width proportional to token count
    # Use log scaling to make the visualization more balanced
    if max_tokens > 0:
        # Ensure small files still have visible bars
        min_width = 15
        # Use logarithmic scaling for better distribution
        log_max = math.log(max_tokens + 1)
        log_current = math.log(tokens + 1)
        bar_width = min_width + int((max_width - min_width) * (log_current / log_max))
    else:
        bar_width = 15

    # Truncate path if needed
    if len(path_str) > bar_width - 4:
        path_str = "..." + path_str[-(bar_width - 7) :]

    # Left-align the path with a small left margin
    left_margin = 2
    right_pad = bar_width - len(path_str) - left_margin
    right_pad = max(0, right_pad)  # Ensure right padding isn't negative

    # Create the bar with the path on it, left-aligned with a small margin
    return f"{bg_color}{' ' * left_margin}{path_str}{' ' * right_pad}{reset}"


def print_color_legend() -> None:
    # Print color legend
    print(" Color Legend:")
    print(
        " \033[42m     \033[0m 1-4,999 tokens       \033[46m     \033[0m 5,000-9,999 tokens"  # noqa: E501
    )
    print(
        " \033[43m     \033[0m 10,000-49,999 tokens \033[45m     \033[0m 50,000-99,999 tokens"  # noqa: E501
    )
    print(" \033[41m     \033[0m 100,000+ tokens\n")
