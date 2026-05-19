import shutil

from .format_tools import (
    COL_ERR,
    COL_WARN,
    COL_INFO,
    COL_RESET,
    COL_BOLD,
    COL_FAINT
)

def format_code_view(code: str, lineno: int, view_range: int) -> str:
    """Return a formatted code view.
    Expects lineno to be 0-based.
    Display only the lines from `lineno - view_range` to `lineno + view_range`."""

    def truncate(line: str, maxwidth: int) -> str:
        """Truncate a string to the given width."""
        return line[:maxwidth - 1] + "…" if len(line) > maxwidth else line

    term_w, _ = shutil.get_terminal_size()

    code_split = code.splitlines()
    start_line: int = max(0, lineno - view_range)
    end_line: int = min(len(code_split), lineno + view_range + 1)
    lines = code_split[start_line:end_line]

    out = []
    max_len = len(str(end_line - 1))
    gutter = max_len + 3

    for n, line in enumerate(lines, start=start_line):
        line = truncate(line, maxwidth=term_w - gutter)

        if n == lineno:
            line = f"{COL_WARN}{COL_BOLD}{n + 1:>{max_len}}{COL_RESET} | {COL_WARN}{line}{COL_RESET}"
        else:
            line = f"{COL_FAINT}{n + 1:>{max_len}}{COL_RESET} | {line}"

        out.append(line)

    return "\n".join(out)

def format_traceback(exc: Exception) -> str:
    return (
        f"we don't talk anymore\n"
        f"error: {exc}"
    )
