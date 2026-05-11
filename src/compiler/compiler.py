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

import io
import sys
import token
import json
import argparse
import subprocess
import tempfile
import tokenize
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

    # ...
    "__my_gospel__": "__all__",
    "marvin_gaye": "from __future__ import",
    "what_are_you_doin_to_me": "breakpoint"
}

COL_WARN = "\033[95m"
COL_ERROR = "\033[91m"
COL_BOLD = "\033[1m"
COL_RESET = "\033[0m"

FSTRING_START = getattr(token, "FSTRING_START", None)
FSTRING_MIDDLE = getattr(token, "FSTRING_MIDDLE", None)
FSTRING_END = getattr(token, "FSTRING_END", None)

@dataclass(frozen=True)
class Args:
    input_path: Path    # .cputh
    output_path: Path   # .py
    force: bool  # overwrite the output file if it already exists
    dangerously_: bool  # skip syntax and type-checking, trailing underscore to avoid keyword collision

@dataclass(frozen=True)
class DiagnosticOutputLine:
    lineno: int
    msg: str
    severity: str  # "error", "warning", "information"

def die(msg: str, exitcode: int = 1) -> NoReturn:
    print(f"{Path(__file__).name}: we don't talk anymore: {msg}", file=sys.stderr)
    sys.exit(exitcode)

class CPuthTranspiler:
    def _transpile_name_token(self, tok: tokenize.TokenInfo, cputh_map: dict[str, str]) -> tokenize.TokenInfo:
        if tok.type != token.NAME:
            return tok
        return tok._replace(string=cputh_map.get(tok.string, tok.string))

    def _transpile_fstring(
            self,
            tokens: list[tokenize.TokenInfo],
            cputh_map: dict[str, str],
            start: int,
        ) -> tuple[list[tokenize.TokenInfo], int]:
        out = [tokens[start]]
        i = start + 1

        while i < len(tokens):
            tok = tokens[i]

            if tok.type == FSTRING_MIDDLE:
                out.append(tok)
                i += 1
                continue

            if tok.type == token.OP and tok.string == "{":
                field_tokens, i = self._transpile_replacement_field(tokens, cputh_map, i)
                out.extend(field_tokens)
                continue

            if tok.type == FSTRING_END:
                out.append(tok)
                return out, i + 1

            out.append(self._transpile_name_token(tok, cputh_map))
            i += 1

        raise SyntaxError("unterminated f-string")

    def _transpile_replacement_field(
            self,
            tokens: list[tokenize.TokenInfo],
            cputh_map: dict[str, str],
            start: int,
        ) -> tuple[list[tokenize.TokenInfo], int]:
        out = [tokens[start]]
        i = start + 1
        nesting = 0

        while i < len(tokens):
            tok = tokens[i]

            if tok.type == FSTRING_START:
                nested_fstring, i = self._transpile_fstring(tokens, cputh_map, i)
                out.extend(nested_fstring)
                continue

            if tok.type == token.OP:
                if tok.string in "([{":
                    nesting += 1
                    out.append(tok)
                    i += 1
                    continue

                if tok.string in ")]}":
                    if tok.string == "}" and nesting == 0:
                        out.append(tok)
                        return out, i + 1

                    nesting -= 1
                    out.append(tok)
                    i += 1
                    continue

                if nesting == 0 and tok.string == "=":
                    out.append(tok)
                    return self._transpile_replacement_field_tail(tokens, cputh_map, out, i + 1)

                if nesting == 0 and tok.string == "!":
                    out.append(tok)
                    i += 1
                    if i < len(tokens):
                        out.append(tokens[i])
                        i += 1
                    return self._transpile_format_spec(tokens, cputh_map, out, i)

                if nesting == 0 and tok.string == ":":
                    out.append(tok)
                    return self._transpile_format_spec(tokens, cputh_map, out, i + 1)

            out.append(self._transpile_name_token(tok, cputh_map))
            i += 1

        raise SyntaxError("unterminated f-string replacement field")

    def _transpile_replacement_field_tail(
            self,
            tokens: list[tokenize.TokenInfo],
            cputh_map: dict[str, str],
            out: list[tokenize.TokenInfo],
            start: int,
        ) -> tuple[list[tokenize.TokenInfo], int]:
        i = start

        if i < len(tokens) and tokens[i].type == token.OP and tokens[i].string == "!":
            out.append(tokens[i])
            i += 1
            if i < len(tokens):
                out.append(tokens[i])
                i += 1

        if i < len(tokens) and tokens[i].type == token.OP and tokens[i].string == ":":
            out.append(tokens[i])
            return self._transpile_format_spec(tokens, cputh_map, out, i + 1)

        if i < len(tokens) and tokens[i].type == token.OP and tokens[i].string == "}":
            out.append(tokens[i])
            return out, i + 1

        raise SyntaxError("invalid f-string replacement field")

    def _transpile_format_spec(
            self,
            tokens: list[tokenize.TokenInfo],
            cputh_map: dict[str, str],
            out: list[tokenize.TokenInfo],
            start: int,
        ) -> tuple[list[tokenize.TokenInfo], int]:
        i = start

        while i < len(tokens):
            tok = tokens[i]

            if tok.type == FSTRING_MIDDLE:
                out.append(tok)
                i += 1
                continue

            if tok.type == token.OP and tok.string == "{":
                nested_field, i = self._transpile_replacement_field(tokens, cputh_map, i)
                out.extend(nested_field)
                continue

            if tok.type == token.OP and tok.string == "}":
                out.append(tok)
                return out, i + 1

            out.append(self._transpile_name_token(tok, cputh_map))
            i += 1

        raise SyntaxError("unterminated f-string format specifier")

    def transpile_tokens(
            self,
            tokens: list[tokenize.TokenInfo],
            cputh_map: dict[str, str],
            start: int = 0,
        ) -> tuple[list[tokenize.TokenInfo], int]:
        out: list[tokenize.TokenInfo] = []
        i = start

        while i < len(tokens):
            tok = tokens[i]

            if tok.type == FSTRING_START:
                fstring_tokens, i = self._transpile_fstring(tokens, cputh_map, i)
                out.extend(fstring_tokens)
                continue

            out.append(self._transpile_name_token(tok, cputh_map))
            i += 1

        return out, i

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

    tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    translated, _ = CPuthTranspiler().transpile_tokens(tokens, CPUTH_MAP)
    return tokenize.untokenize(translated)

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

def format_exc(title: str, exc: Exception, fp: Path, src: str, lineno: int | None) -> str:
    out: list[str] = []

    # Error display
    err_display = f"{COL_ERROR}{COL_BOLD}{title}: {COL_RESET}{COL_ERROR}{exc}{COL_RESET}"
    out.append(err_display)

    # Flavour text and code output
    if lineno is not None:
        out.append(f"file: '{fp}', line {lineno}")
    else:
        out.append(f"file: '{fp}'")

    out.append("we don't talk anymore - how long has this been going on?")
    if lineno is not None:
        out.append("\ncode output:\n")
        out.append(format_code_view(src, lineno=lineno, view_range=2))

    out_str = "\n".join(out)
    return out_str

def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        description ="Compile Charlie Puth code to Python. Why use boring keywords when your source can have feelings?",
        usage=f"{Path(__file__).name} <input_path> <output_path> [-f, --force] [-d, --dangerously]"
    )

    parser.add_argument("input_path", type=Path, help="path to the .cputh file (from where we began)")
    parser.add_argument("output_path", type=Path, help="path to the output .py file (see you again)")
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="overwrite the output file if it already exists"
    )
    parser.add_argument(
        "-d", "--dangerously",
        action="store_true",
        dest="dangerously_",  # attribute name in which to store the attr
        help="skip syntax and type checking. (I knew we would crash at the speed that we were going)"
    )

    # Note: parse_args() handles --help and missing args automatically
    args_raw = parser.parse_args()

    # Input path validation
    if not args_raw.input_path.exists():
        die(f"cannot read from input: no such file: '{args_raw.input_path}'")
    if not args_raw.input_path.is_file():
        die(f"cannot read from input: not a file: '{args_raw.input_path}'")

    # Output parent directory validation
    if not args_raw.output_path.parent.exists():
        die(f"invalid output path: no such parent directory: '{args_raw.output_path.parent}'")

    # Force flag logic
    if args_raw.output_path.exists():
        if args_raw.force:
            print(
                f"{COL_WARN}{COL_BOLD}how long{COL_RESET}{COL_WARN} has '{args_raw.output_path}' been going on? overwriting.{COL_RESET}",
                file=sys.stderr
            )
        else:
            die(f"output file '{args_raw.output_path}' already exists (how long?). use -f or --force to overwrite.")

    # Dangerous flag
    if args_raw.dangerously_:
        print(
            f"{COL_WARN}{COL_BOLD}dangerously{COL_RESET}{COL_WARN}: skipping syntax and type checking. didn't care if the explosion ruined me.{COL_RESET}",
            file=sys.stderr
        )

    return Args(
        input_path=args_raw.input_path,
        output_path=args_raw.output_path,
        force=args_raw.force,
        dangerously_=args_raw.dangerously_
    )

def run(args: Args) -> int:
    try:
        with open(args.input_path, "r", encoding="utf-8") as f:
            cputh = f.read()
    except UnicodeDecodeError:
        die(f"cannot read from input: invalid source encoding: '{args.input_path}'")
        return 1

    try:
        py = compile_cputh_to_py(cputh)
    except tokenize.TokenError as exc:
        print(format_exc(
            title="tokenisation error",
            exc=exc,
            fp=args.input_path,
            src=cputh,
            lineno=exc.args[1][0]
        ))
        return 1

    # Syntax checking
    # If the Python is syntactically incorrect, early abort
    if not args.dangerously_:
        try:
            compile(py, args.input_path.name, mode="exec")
        except SyntaxError as exc:
            print(format_exc(
                title="syntax error",
                exc=exc,
                fp=args.input_path,
                src=py,
                lineno=exc.lineno
            ))
            return 1

    # Type checking
    # Use a temporary file; subprocess doesn't behave consistently on reading from stdin
    if not args.dangerously_:
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

                if diag_output:
                    print(f"\nyou just want attention (static analysis warnings, file: '{args.input_path}'):")
                    print(
                        f"{num_errors} error{"s" if num_errors != 1 else ""}"
                        f", {num_warnings} warning{"s" if num_warnings != 1 else ""}"
                        f", {num_infos} information{"s" if num_infos != 1 else ""}"
                    )
                    for line in diag_output:
                        severity_col = COL_ERROR if line.severity == "error" else COL_WARN
                        print(
                            f"{severity_col}{COL_BOLD}{line.severity}{COL_RESET}: "
                            f"line {line.lineno}: {line.msg}"
                        )

            else:
                print("save your apologies (skipping type checking: pyright not installed - how long has this been going on?)")

    # Finally write the Python code to the output path
    with open(args.output_path, "w", encoding="utf-8") as f:
        f.write(py)

    return 0

def main() -> int:
    args = parse_args()
    try:
        return run(args)
    except KeyboardInterrupt:
        print("\ninterrupted — we don't talk anymore", file=sys.stderr)
        return 130
    except PermissionError as exc:
        print(f"permission denied - it's such a shame: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"file error: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    exitcode = main()
    sys.exit(exitcode)
