import sys
from typing import Any

from cputh.utils.format_exceptions import format_traceback
from cputh._version import version_str
from cputh.compile.compiler import compile_cputh_to_py

# Ctrl-D (EOF) or "we don't talk anymore" to exit the REPL

# bright green, just like what Charlie uses for 'syntax highlighting' his songs
COL_PROMPT = "\033[92m"
COL_BOLD = "\033[1m"
COL_RESET = "\033[0m"

TOP_LEVEL_PROMPT = f"{COL_BOLD}{COL_PROMPT}cputh:{COL_RESET}"
NESTED_PROMPT =    f"{COL_BOLD}{COL_PROMPT}     :{COL_RESET}"

repl_namespace: dict[str, Any] = {}

def run_repl():
    buf: list[str] = []
    in_compound_block: bool = False

    print(f"charlie puth native repl (v{version_str}) - type \"we don't talk anymore\" to exit")

    while True:
        try:
            inp = input(f"{TOP_LEVEL_PROMPT} ")

            if inp == "we don't talk anymore":
                print("see you again.")
                sys.exit(0)

            # Try to evaluate as an expression and print the value if it isn't None
            try:
                compiled_py = compile_cputh_to_py(inp)

                try:
                    code = compile(compiled_py, "<cputh-stdin>", "eval")
                    result = eval(code, repl_namespace)
                    if result is not None:
                        print(repr(result))
                except SyntaxError:
                    # eval only handles expressions; exec handles statements
                    code = compile(compiled_py, "<cputh-stdin>", "exec")
                    exec(code, repl_namespace)

            # Otherwise, execute
            except SyntaxError as e:
                print(format_traceback(e))
            except Exception as e:
                print(format_traceback(e))

            # TODO: add multiline code functionality
        except EOFError:
            print("see you again.")
            sys.exit(0)
        except KeyboardInterrupt:
            print("\nkeyboard interrupt")
            buf.clear()
            continue

if __name__ == "__main__":
    run_repl()
