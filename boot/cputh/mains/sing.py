from pathlib import Path
from cputh.utils.args import Args
from cputh.exceptions.errors import CPuthFileError
from cputh.compile.compiler import compile_cputh_to_py

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

    cputh_code = Path(args.input).read_text()
    py_code = compile_cputh_to_py(cputh_code)

    try:
        exec(py_code, {})
        return 0
    except KeyboardInterrupt:
        return 130
    except BaseException:
        return 1

if __name__ == "__main__":
    main(Args(command="sing"))
