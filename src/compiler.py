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
import json
import argparse
import subprocess
import tempfile
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

COL_WARN = "\033[95m"
COL_ERROR = "\033[91m"
COL_BOLD = "\033[1m"
COL_RESET = "\033[0m"

@dataclass(frozen=True)
class Args:
    input_path: Path    # .cputh
    output_path: Path   # .py
    force: bool  # overwrite the output file if it already exists

@dataclass(frozen=True)
class DiagnosticOutputLine:
    lineno: int
    msg: str
    severity: str  # "error", "warning", "information"

def die(msg: str) -> NoReturn:
    print(f"{Path(__file__).name}: fatal: {msg}", file=sys.stderr)
    sys.exit(1)

def transpile_token(tok: str, cputh_map: dict[str, str]) -> str:
    if tok.startswith(('#', '"""', '"', "'")):
        return tok
    return cputh_map.get(tok, tok)

def parse_diagnostics(json_text: str) -> list[DiagnosticOutputLine]:
    """Parse Pyright JSON output into diagnostic lines."""
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return []

    lines: list[DiagnosticOutputLine] = []
    for diag in data.get("generalDiagnostics", []):
        lineno = diag.get("range", {}).get("start", {}).get("line", 0) + 1  # Pyright is 0-indexed
        msg = diag.get("message", "unknown error")
        severity = diag.get("severity", "error")
        lines.append(DiagnosticOutputLine(lineno=lineno, msg=msg, severity=severity))
    return lines

def check_pyright_installed() -> bool:
    """Check if pyright is available on PATH."""
    try:
        subprocess.run(
            ["pyright", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

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
        if n == lineno:
            line = f"{COL_WARN}{COL_BOLD}{n + 1:>{max_len}}{COL_RESET} | {COL_WARN}{line}{COL_RESET}"
        else:
            line = f"{n + 1:>{max_len}} | {line}"

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
            print(f"{COL_WARN}{COL_BOLD}warning{COL_RESET}: {COL_WARN}overwriting existing file '{args_raw.output_path}'{COL_WARN}", file=sys.stderr)
        else:
            die(f"output file '{args_raw.output_path}' already exists. Use -f or --force to overwrite.")

    return Args(
        input_path=args_raw.input_path,
        output_path=args_raw.output_path,
        force=args_raw.force
    )

def _run(args: Args) -> int:
    try:
        with open(args.input_path, "r", encoding="utf-8") as f:
            cputh = f.read()
    except UnicodeDecodeError:
        die("cannot read from input: invalid source encoding")
        return 1

    py = compile_cputh_to_py(cputh)

    # Validate the compiled Python
    # If the Python is syntactically incorrect, early abort
    try:
        compile(py, args.input_path.name, mode="exec")
    except SyntaxError as exc:
        out: list[str] = []

        # Error display
        err_displ = f"{COL_ERROR}{COL_BOLD}syntax error: {COL_RESET}{COL_ERROR}{exc}{COL_RESET}"
        out.append(err_displ)

        # Flavour text and code output
        if exc.lineno is not None:
            out.append(f"file: '{args.input_path}', line {exc.lineno}")
        else:
            out.append(f"file: '{args.input_path}'")
        out.append("we don't talk anymore - how long has this been going on?")
        if exc.lineno is not None:
            out.append("\nPython output:\n")
            out.append(format_code_view(py, lineno=exc.lineno, view_range=2))

        out_str = "\n".join(out)
        print(out_str, file=sys.stderr)
        return 1

    # Use a temporary file; subprocess doesn't behave consistently on reading from stdin
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=True) as tempf:
        tempf.write(py)
        tempf.flush()

        if check_pyright_installed():
            proc = subprocess.run(
                ["pyright", "--outputjson", tempf.name],
                capture_output=True,
            )

            # Parse JSON from stdout; Pyright writes JSON to stdout
            text = proc.stdout.decode("utf-8", errors="replace")
            diag_output: list[DiagnosticOutputLine] = parse_diagnostics(text)

            # Get summary statistics
            total_msgs = len(diag_output)
            num_errors = sum(1 for d in diag_output if d.severity == "error")
            num_warnings = sum(1 for d in diag_output if d.severity == "warning")
            num_infos = total_msgs - num_errors - num_warnings

            error_sufx = "s" if num_errors != 1 else ""
            warning_sufx = "s" if num_warnings != 1 else ""
            info_sufx = "s" if num_infos != 1 else ""

            if diag_output:
                print("\nyou just want attention (static analysis warnings):")
                print(
                    f"{num_errors} error{error_sufx}"
                    f", {num_warnings} warning{warning_sufx}"
                    f", {num_infos} information{info_sufx}"
                )
                for line in diag_output:
                    severity_col = COL_ERROR if line.severity == "error" else COL_WARN
                    print(
                        f"{severity_col}{COL_BOLD}{line.severity}{COL_RESET}: "
                        f"line {line.lineno}: {line.msg}"
                    )

        else:
            print("save your apologies (pyright not installed, skipping type checking)")

    # Finally write the Python code to the output path
    with open(args.output_path, "w", encoding="utf-8") as f:
        f.write(py)

    return 0

def main() -> int:
    args = parse_args()
    try:
        return _run(args)
    except KeyboardInterrupt:
        print("\ninterrupted — we don't talk anymore", file=sys.stderr)
        return 130
    except PermissionError as exc:
        print(f"permission denied: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"file error: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    exitcode = main()
    sys.exit(exitcode)
