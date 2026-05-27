#!/usr/bin/env python3
# The shebang retains its functionality when compiled to Python

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
import os
import sys
import token
import json
import argparse
import subprocess
import shutil
import tokenize
from dataclasses import dataclass
from pathlib import Path

_compile_dir = Path(os.environ["CPUTH_REF_DIR"]) if "CPUTH_REF_DIR" in os.environ else Path(__file__).parents[3] / "dist"
sys.path.insert(0, str(_compile_dir))

from cputh.utils.format_exceptions import format_code_view
from cputh.compile.compiler import compile_cputh_to_py
from cputh.compile.type_check import run_type_checking
from cputh.utils.utils import check_pyright_installed
from cputh.utils.args import Args
from cputh.exceptions.errors import (
    CPuthException,
    CPuthSyntaxError,
    CPuthTokenError,
    CPuthFileError,
)

COL_FAINT = "\033[2m"
COL_WARN = "\033[95m"
COL_ERROR = "\033[91m"
COL_BOLD = "\033[1m"
COL_RESET = "\033[0m"

# TODO: reintroduce advanced file permission checking logic
# this could be done with a function: check_file_status(fp: Path) -> FileStatus
# FileStatus would be a StrEnum with: EXIST, NOEXIST, EXIST_NOPERM, NOEXIST_PARENT_NOPERM.

# TODO: merge this with the format_exc from format_exceptions.cputh;
# maybe make a general format_exc that can handle both CPuth and
# Python exceptions, and then have a wrapper for each that calls
# the general one with the appropriate parameters?
def format_exc(
        exc: CPuthException, title: str,
        flavour_text: str | None = None, src_title: str | None = None
    ) -> str:
    """Return a formatted CPuth exception message. Expects 0-based lineno values."""

    out: list[str] = []

    # Error header
    err_header = f"{COL_ERROR}{COL_BOLD}{title}: {COL_RESET}{COL_ERROR}{exc}{COL_RESET}"
    out.append(err_header)

    # File and line number
    if isinstance(exc, CPuthSyntaxError) and exc.lineno is not None:
        if exc.fp is not None:
            out.append(f"file: '{exc.fp}', line {exc.lineno + 1}")
        else:
            out.append(f"line {exc.lineno + 1}")
    elif exc.fp is not None:
        out.append(f"file: '{exc.fp}'")

    # Flavour text
    if flavour_text:
        out.append(flavour_text)

    # Code view
    if isinstance(exc, CPuthSyntaxError) and exc.src is not None and exc.lineno is not None:
        out.append(f"\ncode ({src_title}):")
        out.append(format_code_view(exc.src, lineno=exc.lineno, view_range=2))

    out_str = "\n".join(out)
    return out_str

def validate_args(args: Args) -> None:
    """Validate that command-line args are syntactically correct and that
    input and output files exist. Throws CPuthFileError if validation fails."""

    # Both input and output files are required.
    if args.input is None:
        raise CPuthFileError("missing argument: input file")
    if args.output is None:
        raise CPuthFileError("missing argument: output file")
    if args.dir_ is not None and not args.dir_.exists():
        raise CPuthFileError(f"no such compiler directory: '{args.dir_}'")
    if args.dir_ is not None and not args.dir_.is_dir():
        raise CPuthFileError(f"compiler reference path is not a directory: '{args.dir_}'")

    # Input file and output file's parent directory must both exist.
    if not args.input.exists():
        raise CPuthFileError("no such input file")
    if not args.output.parent.exists():
        raise CPuthFileError("no such output parent directory")

    # If output file exists, --force is required to overwrite it.
    if args.output.exists():
        if args.force:
            print(
                f"{COL_WARN}{COL_BOLD}how long{COL_RESET}{COL_WARN} has '{args.output}' been going on? overwriting.{COL_RESET}",
                file=sys.stderr
            )
        else:
            raise CPuthFileError(f"output file '{args.output}' already exists (how long?). use -f or --force to overwrite)")

    # Dangerous flag
    if args.dangerously_:
        print(
            f"{COL_WARN}{COL_BOLD}dangerously{COL_RESET}{COL_WARN}: skipping syntax and type checking. didn't care if the explosion ruined me.{COL_RESET}",
            file=sys.stderr
        )

def run(args: Args) -> None:
    """Attempt to run the compiler with the provided arguments.
    Throws (different kinds of) CPuthException on failure."""

    validate_args(args)

    # These asserts are safe because validate_args would have thrown if either of these is None
    # They exist purely to prevent Pyright from flipping the table.
    # Static analysers are like those old stickler teachers who would make you write
    # "I will not talk in class" 100 times on the board, except instead of talking
    # in class, it's "I will check for None before accessing this variable" 100 times on the code.
    assert args.input is not None
    assert args.output is not None

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            cputh = f.read()
    except UnicodeDecodeError:
        raise CPuthSyntaxError(
            f"cannot read from input: invalid source encoding: '{args.input}'",
            fp=args.input
        )

    py = compile_cputh_to_py(cputh)

    # Syntax checking
    # If the Python is syntactically incorrect, early abort...unless if the
    # user enters the -d or --dangerously flag.
    # Knew we would crash at the speed that we were going; didn't care if the explosion ruined me
    if not args.dangerously_:
        try:
            compile(py, args.input.name, mode="exec")
        except SyntaxError as exc:
            raise CPuthSyntaxError(
                msg=str(exc),
                fp=args.input,
                src=py,
                lineno=exc.lineno - 1 if exc.lineno is not None else None,
            )

    # Write the Python code to the output path
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(py)

    # Finally, run type checking on the output
    if not args.dangerously_:
        run_type_checking(py_path=args.output, display_input_path=args.input)

def main(args: Args) -> int:
    try:
        run(args)
        return 0
    except CPuthFileError as exc:
        print(format_exc(title="file error", exc=exc), file=sys.stderr)
        return 1
    except CPuthTokenError as exc:
        exc.fp = args.input
        print(format_exc(exc=exc, title="token error", flavour_text="how long has this been tokenising wrong?", src_title="cputh side"), file=sys.stderr)
        return 1
    except CPuthSyntaxError as exc:
        exc.fp = args.input
        print(format_exc(exc=exc, title="syntax error", flavour_text="we don't compile anymore", src_title="python side"), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(f"\n{COL_BOLD}{COL_ERROR}interrupted{COL_RESET}{COL_ERROR} — we don't talk anymore{COL_RESET}", file=sys.stderr)
        return 130
    except PermissionError as exc:
        print(f"{COL_BOLD}{COL_ERROR}permission denied{COL_RESET}{COL_ERROR} - it's such a shame: {exc}{COL_RESET}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"{COL_BOLD}{COL_ERROR}file error{COL_RESET}{COL_ERROR}: {exc}{COL_RESET}", file=sys.stderr)
        return 1
