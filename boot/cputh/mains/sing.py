import linecache

from pathlib import Path
from cputh.utils.args import Args
from cputh.exceptions.errors import CPuthFileError
from cputh.compile.compiler import compile_cputh_to_py
from cputh.utils.format_exceptions import format_exc
from cputh.utils.flags import DEFAULT_STATE

def validate_args(args: Args) -> None:
    if not args.input is not None:
        raise CPuthFileError("Missing argument: input file path is required")

    if not args.input.exists():
        raise CPuthFileError(f"No such file: '{args.input}'")
    if not args.input.is_file():
        raise CPuthFileError(f"Not a file: '{args.input}'")

def main(args: Args) -> int:
    try:
        validate_args(args)
    except Exception as exc:
        # Argument validation exception
        fmted_exc = format_exc(exc, is_runtime_err=False)
        print(fmted_exc)
        return 1

    assert args.input is not None

    cputh_code = args.input.read_text()
    filename_str = str(args.input.resolve())

    try:
        py_code, _ = compile_cputh_to_py(cputh_code, DEFAULT_STATE)
        code_obj = compile(py_code, filename_str, "exec")
    except Exception as exc:
        # Compile-time error
        setattr(exc, "fp", args.input)  # yeah we're setting a custom attr to a builtin Exception class, too bad!
        fmted_exc = format_exc(exc, is_runtime_err=False)
        print(fmted_exc)
        return 1

    # Using linecache to cache filenames before starting
    linecache.cache[filename_str] = (
        len(cputh_code),
        None,
        [line + "\n" for line in cputh_code.splitlines()],
        filename_str,
    )

    EXEC_NS = {
        "__name__": "__main__",
        "__file__": str(args.input),
        "__package__": None,
        "__doc__": None
    }

    try:
        exec(code_obj, EXEC_NS)
        return 0
    except KeyboardInterrupt as exc:
        fmted_exc = format_exc(exc, is_runtime_err=True)
        print(fmted_exc)
        return 130
    except BaseException as exc:
        fmted_exc = format_exc(exc, is_runtime_err=True)
        print(fmted_exc)
        return 1

if __name__ == "__main__":
    main(Args(command="sing"))
