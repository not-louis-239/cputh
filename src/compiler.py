#!/usr/bin/env python3
# The shebang retains its functionality when transpiled to Python

# Copyright 2026 Louis Masarei-Boulton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys
import argparse
from dataclasses import dataclass
from typing import NoReturn
from pathlib import Path

CPUTH_MAP: dict[str, str] = {
    # imports
    "from_where_we_began": "from",
    "get_it_on": "import",

    # conditionals
    "attention": "if",
    "left_right_left": "elif",
    "no_matter_where_you_go": "else",

    # membership / logic
    "i_still_look_at_you_the_same": "is",
    "all_up_on_ya": "in",
    "nothing_left": "not",
    "come_along_with_me": "and",
    "share_our_fears": "or",

    # loops
    "how_long": "while",
    "runnin_round": "for",
    "move_on": "continue",
    "we_dont_talk_anymore": "break",
    "slow_it_down": "pass",

    # functions / classes
    "then_theres_you": "class",
    "one_call_away": "def",
    "smaller_talks": "lambda",
    "done_for_me": "return",
    "cheating_on_you": "yield",

    # scope
    "this_whole_world": "global",
    "not_alone": "nonlocal",
    "erase": "del",

    # async
    "i_still_can_hear_you": "async",
    "it_wont_be_long": "await",

    # exceptions
    "promise_me": "assert",
    "dangerously": "try",
    "please_forgive_me": "except",
    "see_you_again": "finally",
    "blame_myself": "raise",

    # constants
    "TheWayIAm": "True",
    "ShouldveKnown": "False",
    "Nothing": "None",

    # i/o
    "everyone_knows": "print",
    "tell_me_honestly": "input",

    # data structures
    "lightswitch": "bool",
    "memories": "list",
    "mind": "dict",

    # context
    "stay_with_me": "with",
    "call_me": "as",
}

# Captures: strings, comments, identifiers/keywords, whitespace, and symbols, in that order
TOKEN_RE = re.compile(
    r'""".*?"""|'               # docstrings
    r'"(?:\\.|[^"\\])*"|'       # double-quoted strings
    r"'(?:\\.|[^'\\])*'|"       # single-quoted strings
    r'#[^\n]*|'                 # comments - must be before language tokens
    r'[A-Za-z_][A-Za-z0-9_]*|'  # identifiers/keywords
    r'[^\S\n]+|'                # horizontal whitespace
    r'\n|'                      # newlines
    r'.',                       # everything else
    re.DOTALL  # required for .*? to permeate newlines, otherwise docstrings break
)

@dataclass(frozen=True)
class Args:
    input_path: Path    # .cputh
    output_path: Path   # .py
    force: bool  # overwrite the output file if it already exists

def die(msg: str) -> NoReturn:
    print(f"{Path(__file__).name}: fatal: {msg}", file=sys.stderr)
    sys.exit(1)

def transpile_token(tok: str, cputh_map: dict[str, str]) -> str:
    if tok.startswith(('#', '"""', '"', "'")):
        return tok
    return cputh_map.get(tok, tok)

def compile_cputh_to_py(text: str) -> str:
    """Compile CPuth source to Python."""

    # This assumes TOKEN_RE captures everything, including whitespace/newlines
    tokens = TOKEN_RE.findall(text)

    # Map tokens: If it's a Puth-lyric, swap it.
    # If it's whitespace or unknown, keep it exactly as it was.
    translated = [
        transpile_token(tok, CPUTH_MAP)
        for tok in tokens
        if tok is not None
    ]

    # Join them with NO extra logic.
    # The original spaces/newlines from the input are tokens too!
    return "".join(translated)  # type: ignore

def format_code_view(code: str, lineno: int, view_range: int) -> str:
    """Return a formatted compiler error message

    Display only the lines from lineno - view_range to lineno + view_range."""

    lineno -= 1  # SyntaxError line numbers are 1-based

    code_split = code.splitlines()
    start_line: int = max(0, lineno - view_range)
    end_line: int = min(len(code_split), lineno + view_range + 1)
    lines = code_split[start_line:end_line]

    out = []
    max_len = len(str(end_line - 1))
    for n, line in enumerate(lines, start=start_line):
        line = f"{n:>{max_len}} | {line}"

        if n == lineno:
            line = "\033[95m" + line + "\033[0m"

        out.append(line)

    return "\n".join(out)

def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        description ="Compile Charlie Puth code to Python.",
        usage=f"{Path(__file__).name} <input_path> <output_path> [-f, --force]"
    )

    parser.add_argument("input_path", type=Path, help="Path to the .cputh file")
    parser.add_argument("output_path", type=Path, help="Path to the output .py file")
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite the output file if it already exists"
    )

    # Note: parse_args() handles --help and missing args automatically
    args_raw = parser.parse_args()

    # Input path validation
    if not args_raw.input_path.exists():
        die(f"cannot read from input: no such file: {args_raw.input_path}")
    if not args_raw.input_path.is_file():
        die(f"cannot read from input: invalid file: {args_raw.input_path}")

    # Output parent directory validation
    if not args_raw.output_path.parent.exists():
        die(f"invalid output file: no such parent directory: {args_raw.output_path.parent}")

    # Force flag logic
    if args_raw.output_path.exists():
        if args_raw.force:
            print(f"\033[93m\033[1mwarning\033[0m\033[33m: overwriting existing file '{args_raw.output_path}'\033[0m", file=sys.stderr)
        else:
            die(f"output file '{args_raw.output_path}' already exists. Use -f or --force to overwrite.")

    return Args(
        input_path=args_raw.input_path,
        output_path=args_raw.output_path,
        force=args_raw.force
    )

def main() -> None:
    args = parse_args()

    with open(args.input_path, "r") as f:
        cputh = f.read()

    py = compile_cputh_to_py(cputh)

    # Validate the compiled Python
    # If the Python is syntactically incorrect, don't write to the output file
    try:
        compile(py, args.input_path.name, mode="exec")
    except SyntaxError as exc:
        print(f"\033[1m\033[91msyntax error: \033[0m\033[31m{exc}\033[0m", file=sys.stderr)
        print(f"Code was not written to output file.")
        print("\nPython output:\n")
        if exc.lineno is not None:
            print(format_code_view(py, lineno=exc.lineno, view_range=2))
        sys.exit(1)

    with open(args.output_path, "w") as f:
        f.write(py)

if __name__ == "__main__":
    main()
