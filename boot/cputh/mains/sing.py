import linecache
import importlib.abc
import sys
import os

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

    # Minimal import hook so Python can import .cputh modules while running
    # in sing mode. This lets CPuth source files be imported from the
    # filesystem (e.g. tests/exec/import_test_package.cputh).
    class _CPuthLoader(importlib.abc.Loader):
        def __init__(self, path: str, is_package: bool):
            self.path = path
            self.is_package = is_package

        def create_module(self, spec):
            return None

        def exec_module(self, module):
            src = Path(self.path).read_text()
            py_code, _ = compile_cputh_to_py(src, DEFAULT_STATE)
            code_obj = compile(py_code, self.path, "exec")
            module.__file__ = self.path
            if self.is_package:
                module.__package__ = module.__name__
                module.__path__ = [os.path.dirname(self.path)]
            else:
                module.__package__ = module.__name__.rpartition(".")[0]
            exec(code_obj, module.__dict__)


    class _CPuthFinder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path, target=None):
            # Determine candidate search paths
            search_paths = list(path) if path is not None else list(sys.path)

            mod_rel = fullname.replace('.', os.sep)

            # Check for package (__init__.cputh)
            for base in search_paths:
                pkg_init = os.path.join(base, mod_rel, "__init__.cputh")
                if os.path.isfile(pkg_init):
                    loader = _CPuthLoader(pkg_init, is_package=True)
                    from importlib.machinery import ModuleSpec
                    spec = ModuleSpec(fullname, loader, is_package=True)
                    spec.origin = pkg_init
                    spec.submodule_search_locations = [os.path.join(base, mod_rel)]
                    return spec

            # Check for module file <mod>.cputh
            for base in search_paths:
                candidate = os.path.join(base, f"{mod_rel}.cputh")
                if os.path.isfile(candidate):
                    loader = _CPuthLoader(candidate, is_package=False)
                    from importlib.machinery import ModuleSpec
                    spec = ModuleSpec(fullname, loader, is_package=False)
                    spec.origin = candidate
                    return spec

            return None

    # Insert our finder early so .cputh imports resolve while executing the
    # compiled CPuth code.
    sys.meta_path.insert(0, _CPuthFinder())

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
