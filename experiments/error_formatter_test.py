# testing a new error formatter function for non-runtime errors

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "boot"))

from cputh.exceptions.errors import CPuthException, CPuthSyntaxError
from cputh.utils.format_tools import COL_BOLD, COL_ERR, COL_RESET
from cputh.utils.format_exceptions import format_code_view, ERR_WRAPPER_NAMES


def format_exc(exc: Exception, flavour_text: str | None = None) -> str:
    """Return a formatted CPuth exception message. Expects 0-based lineno values."""

    out: list[str] = []
    title = ERR_WRAPPER_NAMES.get(type(exc), "error")

    # Error header
    err_header = f"{COL_ERR}{COL_BOLD}{title}: {COL_RESET}{COL_ERR}{exc}{COL_RESET}"
    out.append(err_header)

    # File and line number
    if isinstance(exc, CPuthSyntaxError) and exc.lineno is not None:
        if exc.fp is not None:
            out.append(f"file: '{exc.fp}', line {exc.lineno + 1}")
        else:
            out.append(f"line {exc.lineno + 1}")
    elif isinstance(exc, CPuthException) and exc.fp is not None:
        out.append(f"file: '{exc.fp}'")

    # Flavour text
    if flavour_text:
        out.append(flavour_text)

    # Code view
    if isinstance(exc, CPuthSyntaxError) and exc.src is not None and exc.lineno is not None:
        out.append(format_code_view(exc.src, lineno=exc.lineno, view_range=2))

    out_str = "\n".join(out)
    return out_str

def main():
    src = """
    one_call_away main():
        x = 5
        y = 3
        result = 0

        how_long y > 0
            result += x
            y--

        done_for_me result

    hear_me_out:
        r = main()
        everyone_knows(f"result: {r}")
    """

    test_exc = CPuthSyntaxError("expected ':'", fp=Path("test.cputh"), src=src, lineno=6)

    print(format_exc(exc=test_exc, flavour_text="we don't compile anymore"))

if __name__ == "__main__":
    main()
