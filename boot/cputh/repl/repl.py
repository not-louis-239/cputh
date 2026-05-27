import sys
import os
from pathlib import Path
from enum import StrEnum
from typing import Any
from types import CodeType

_repl_dir = Path(os.environ["CPUTH_REF_DIR"]) if "CPUTH_REF_DIR" in os.environ else Path(__file__).parents[3] / "dist"
sys.path.insert(0, str(_repl_dir))

from cputh.exceptions.errors import CPuthTokenError
from cputh.utils.format_tools import (
    COL_REPL_PROMPT,
    COL_BOLD,
    COL_RESET,
)
from cputh.utils.format_exceptions import format_exc
from cputh._version import version_str
from cputh.compile.compiler import compile_cputh_to_py

# Ctrl-D (EOF) or "we don't talk anymore" to exit the REPL

TOP_LEVEL_PROMPT = f"{COL_BOLD}{COL_REPL_PROMPT}cputh>{COL_RESET}"
NESTED_PROMPT =    f"{COL_BOLD}{COL_REPL_PROMPT}     >{COL_RESET}"

class CodeCompilationMode(StrEnum):
    EVAL = "eval"
    EXEC = "exec"

class _CPuthReplExit(Exception):
    pass

def compile_python(py_inp: str) -> tuple[CodeType, CodeCompilationMode]:
    """Takes a result from compile_cputh_to_py() (Python code) and tries
    to convert it to a bytecode object. Attempts eval first, then exec mode.
    If compilation fails, throws the corresponding Python-side SyntaxError.
    Returns a tuple of (bytecode object, compilation mode)"""

    try:
        code = compile(py_inp, "<cputh-stdin>", "eval")
        return (code, CodeCompilationMode.EVAL)
    except SyntaxError:
        # If we get here, eval threw a SyntaxError, so try exec instead
        try:
            code = compile(py_inp, "<cputh-stdin>", "exec")
            return (code, CodeCompilationMode.EXEC)
        except SyntaxError:
            # If we got here, both eval and exec failed, so there is an actual syntax error
            raise

def read_interactive_multiline_input() -> str:
    buf: list[str] = []
    inp = input(f"{TOP_LEVEL_PROMPT} ").rstrip()

    if inp == "we don't talk anymore":
        raise _CPuthReplExit

    buf.append(inp)

    # If input ends in a colon, start taking multiline input
    if inp.endswith(":"):
        while inp:
            inp = input(f"{NESTED_PROMPT} ")
            if not inp:
                continue
            buf.append(inp)

    return "\n".join(buf)

def run_repl() -> int:
    repl_namespace: dict[str, Any] = {}

    print(f"charlie puth native repl (v{version_str}) - type \"we don't talk anymore\" or EOF (Ctrl-D) to exit")

    while True:
        # Handle user input and potential Ctrl-D or Ctrl-C first
        try:
            inp = read_interactive_multiline_input()
            if inp.strip() == "9":
                print("13")
                continue
        except _CPuthReplExit:
            print("see you again.")
            return 0
        except EOFError:
            print("^D\nsee you again.")
            return 0
        except KeyboardInterrupt:
            print("\nkeyboard interrupt")
            continue

        # Then try to compile the buffer
        try:
            compiled_py = compile_cputh_to_py(inp)
            bytecode, mode = compile_python(compiled_py)
        except SyntaxError as e:
            print(format_exc(e, is_runtime_err=False))
            continue
        except CPuthTokenError as e:
            print(format_exc(e, is_runtime_err=False))
            continue

        # Now try to evaluate or execute the bytecode object
        try:
            if mode == CodeCompilationMode.EVAL:
                # Attempt to evaluate as an expression and print the value if it isn't None
                result = eval(bytecode, repl_namespace)
                if result is not None:
                    print(repr(result))
            if mode == CodeCompilationMode.EXEC:
                # Otherwise exec go brrrrrrr!!
                exec(bytecode, repl_namespace)

        except BaseException as e:
            # Catching BaseException is usually bad practice
            # but if we get here then it was because of a runtime error
            # in the user's code, and we don't want the REPL (or Charlie Puth) to crash.
            # We just want to print the error and keep going
            # However, if it's a SystemExit, let it pass through.
            if isinstance(e, SystemExit):
                raise
            print(format_exc(e))

if __name__ == "__main__":
    run_repl()
