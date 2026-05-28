import shutil
import traceback
import tokenize
import linecache

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
ERR_WRAPPER_NAMES: dict[type[BaseException], str] = {
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

    RuntimeError: "runtime error",
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
    frames_lines: list[str] = []

    if tb is not None:
        all_frames = traceback.extract_tb(tb)

        # Skip the first frame which is internal
        user_frames = all_frames[1:] if len(all_frames) > 1 else all_frames

        # Loop through only the user-land frames
        for frame in user_frames:
            filename = frame.filename
            lineno = frame.lineno
            name = frame.name

            # Check if native traceback found the line.
            # If not, violently rip it directly out of the memory linecache
            line_code = frame.line
            if not line_code:
                if lineno is not None:  # must check if isn't None, otherwise default to fallback
                    line_code = linecache.getline(filename, lineno)
                else:
                    line_code = ""

            # Clean up spacing or provide a fallback if it's truly empty
            line_code = line_code.strip() if line_code.strip() else "..."

            frames_lines.append(
                f"  at {COL_WARN}'{filename}'{COL_RESET}, line {COL_WARN}{lineno}{COL_RESET}, in {COL_WARN}{name}{COL_RESET}\n"
                f"    {line_code}"
            )

    # Join all inner frames together with a clean spacing layout
    tb_body = "\n".join(frames_lines)
    if tb_body:
        tb_body += "\n"

    return tb_body

def _format_non_runtime_err(exc: BaseException) -> str:
    """Return a formatted CPuth exception message. Expects 0-based lineno values."""

    # TODO: Fix bug where it can possibly break in REPL where input lines don't match up,
    # e.g. you make a func of multiple lines, then call it in 1 line, linecache
    # attempts to look up the line and prints the wrong line or prints a line
    # that it can't see.

    out: list[str] = []
    title = ERR_WRAPPER_NAMES.get(type(exc), "error")

    out.append("we don't talk anymore")

    # Error header
    err_header = f"{COL_ERR}{COL_BOLD}{title}: {COL_RESET}{COL_ERR}{exc}{COL_RESET}"
    out.append(err_header)

    # File and line number
    if isinstance(exc, CPuthSyntaxError) and exc.lineno is not None:
        if exc.fp is not None:
            out.append(f"at '{exc.fp}', line {exc.lineno + 1}")
        else:
            out.append(f"line {exc.lineno + 1}")
    elif isinstance(exc, CPuthException) and exc.fp is not None:
        out.append(f"at '{exc.fp}'")

    # Code view
    if (
            isinstance(exc, CPuthSyntaxError)
            and exc.src is not None
            and exc.lineno is not None
        ):
        out.append(format_code_view(exc.src, lineno=exc.lineno, view_range=2))

    out_str = "\n".join(out)
    return out_str

def _format_runtime_err(exc: BaseException) -> str:
    body = _format_traceback_body(exc)

    footer_line_prefix = f"{COL_BOLD}{COL_WARN}{get_err_wrapper_name(exc)}{COL_RESET}"
    if (str_exc := str(exc)):
        footer_line = f"{footer_line_prefix}: {COL_WARN}{str_exc}{COL_RESET}"
    else:
        footer_line = f"{footer_line_prefix}"

    return (
        f"we don't talk anymore (most recent call last)\n"
        f"{body}"
        f"{footer_line}"
    )

def format_exc(
        exc: BaseException, is_runtime_err: bool = True
    ) -> str:
    # handle compile time errors first
    if not is_runtime_err:
        return _format_non_runtime_err(exc)
    return _format_runtime_err(exc)
