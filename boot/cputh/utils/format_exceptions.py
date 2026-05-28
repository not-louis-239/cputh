import shutil
import traceback
import tokenize

from cputh.exceptions.errors import (
    CPuthException,
    CPuthSyntaxError,
    CPuthTokenError,
    CPuthFileError
)
from cputh.utils.format_tools import (
    COL_ERR,
    COL_WARN,
    COL_INFO,
    COL_RESET,
    COL_BOLD,
    COL_FAINT
)

# Charlie's names for errors - most specific must come first
ERR_WRAPPER_NAMES = {
    UnboundLocalError: "unbound local error",          # NameError
    TabError: "tab error",                             # IndentationError
    FileNotFoundError: "file error",                   # OSError
    IsADirectoryError: "is a directory error",         # OSError
    NotADirectoryError: "not a directory error",       # OSError
    PermissionError: "permission error",               # OSError
    ModuleNotFoundError: "module not found error",     # ImportError
    ZeroDivisionError: "zero division error",          # ArithmeticError
    OverflowError: "overflow error",                   # ArithmeticError
    FloatingPointError: "floating point error",        # ArithmeticError
    IndexError: "index error",                         # LookupError
    KeyError: "key error",                             # LookupError
    IndentationError: "indentation error",             # SyntaxError

    NameError: "name error",
    SyntaxError: "syntax error",
    ImportError: "import error",
    ArithmeticError: "math error",
    LookupError: "lookup error",
    OSError: "os error",
    RuntimeError: "runtime error",

    AssertionError: "assertion error",
    AttributeError: "attribute error",
    EOFError: "eof error",
    MemoryError: "memory error",
    RecursionError: "depth error",
    StopIteration: "stop iteration",
    TimeoutError: "timeout error",
    TypeError: "type error",
    ValueError: "value error",
    KeyboardInterrupt: "keyboard interrupt",

    tokenize.TokenError: "token error",
    CPuthTokenError: "token error",
    CPuthFileError: "file error",
    CPuthSyntaxError: "syntax error",
    CPuthException: "error",

    Exception: "error",
}

def get_err_wrapper_name(err: BaseException) -> str:
    for class_ in ERR_WRAPPER_NAMES:
        if isinstance(err, class_):
            return ERR_WRAPPER_NAMES[class_]
    return "error"

def format_code_view(code: str, lineno: int, view_range: int) -> str:
    """Return a formatted code view for a block of code.
    Expects lineno to be 0-based.
    Do not use for a single line.
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

def _format_traceback_body(exc: BaseException) -> str:
    tb = exc.__traceback__
    frames_lines = []

    if tb is not None:
        all_frames = traceback.extract_tb(tb)

        # Skip the first frame which is internal
        user_frames = all_frames[1:] if len(all_frames) > 1 else all_frames

        # Loop through only the user-land frames
        for frame in user_frames:
            filename = frame.filename
            lineno = frame.lineno
            name = frame.name
            line_code = frame.line.strip() if frame.line else "..."

            frames_lines.append(
                f"  at '{filename}', line {lineno}, in '{name}'\n"
                f"    {line_code}"
            )

    # Join all inner frames together with a clean spacing layout
    tb_body = "\n".join(frames_lines)
    if tb_body:
        tb_body += "\n"

    return tb_body

def _format_non_runtime_err(exc: BaseException) -> str:
    # TODO: Show code view (the function's already there!)

    if str(exc):
        footer_line = f"{get_err_wrapper_name(exc)}: {exc}"
    else:
        footer_line = f"{get_err_wrapper_name(exc)}"

    return (
        f"we don't talk anymore\n"
        f"{footer_line}"
    )

def _format_runtime_err(exc: BaseException) -> str:
    body = _format_traceback_body(exc)

    if str(exc):
        footer_line = f"{get_err_wrapper_name(exc)}: {exc}"
    else:
        footer_line = f"{get_err_wrapper_name(exc)}"

    return (
        f"we don't talk anymore (most recent call last)\n"
        f"{body}"
        f"{footer_line}"
    )

def format_exc(exc: BaseException, is_runtime_err: bool = True) -> str:
    # handle compile time errors first
    if not is_runtime_err:
        return _format_non_runtime_err(exc)
    return _format_runtime_err(exc)
