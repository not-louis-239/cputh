from pathlib import Path
from cputh.utils.args import Args
from cputh.exceptions.errors import CPuthFileError
from cputh.compile.compiler import compile_cputh_to_py
from cputh.utils.format_exceptions import format_exc

def validate_args(args: Args) -> None:
    if not args.input is not None:
        raise CPuthFileError("Missing argument: input file path is required")

    if not args.input.exists():
        raise CPuthFileError(f"No such file: '{args.input}'")
    if not args.input.is_file():
        raise CPuthFileError(f"Not a file: '{args.input}'")

def main(args: Args) -> int:
    validate_args(args)

    assert args.input is not None

    cputh_code = args.input.read_text()

    try:
        py_code = compile_cputh_to_py(cputh_code)
    except Exception as exc:
        fmted_exc = format_exc(exc, is_runtime_err=False)
        print(fmted_exc)
        return 1

    try:
        exec(py_code, {"__name__": "__main__"})
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
