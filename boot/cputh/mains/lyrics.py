import sys

from cputh.utils.args import Args
from cputh.compile.load_gram import load_grammar_file
from cputh.utils.format_tools import (
    COL_KW_CPUTH,
    COL_KW_PY,
    COL_RESET
)
from cputh._version import version_str

COL_HEADER = "\033[93m\033[1m"

def display_kw(cputh_kw: str, py_kw: str, max_len: int) -> str:
    return f"* {COL_KW_CPUTH}{cputh_kw:<{max_len}}{COL_RESET} = {COL_KW_PY}{py_kw}{COL_RESET}"

def main(args: Args) -> int:
    print(
        f"cputh native help (v{version_str})"
        "\n\nYou just want attention; your night has just begun. Maybe it's that unmatched paren on line 42."
        "\nYeah you just want attention; I knew from line 1. You're just making sure I can never compile through."
        f"\n\nleft side  = {COL_KW_CPUTH}CPuth{COL_RESET}"
        f"\nright side = {COL_KW_PY}Python{COL_RESET}"
        f"\n\nAs of CPuth v0.3.1+, using Nothing as None is deprecated; use EmptyCups instead.\nThe 'Nothing' keyword will be removed in v0.5.0"
    )

    gram = load_grammar_file()

    keywords = []
    for cat_name, cat_contents in gram.items():
        if cat_name == "_":
            continue
        keywords.extend(cat_contents.keys())
    max_len = max(len(kw) for kw in keywords)

    for cat_name, cat_contents in gram.items():
        if cat_name == "_":
            continue

        print(f"\n{COL_HEADER}{cat_name.replace('_', ' ')}{COL_RESET}")
        for cputh, py in cat_contents.items():
            # using .strip() for visual alignment even though some
            # conversions have spaces on the Python side internally
            print(display_kw(cputh, py.strip(), max_len=max_len))

    return 0

if __name__ == "__main__":
    exitcode = main(Args(command="lyrics"))
    sys.exit(exitcode)
