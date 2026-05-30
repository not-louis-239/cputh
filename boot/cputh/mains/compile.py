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

from cputh.utils.format_exceptions import _format_non_runtime_err
from cputh.compile.compiler import compile_cputh_to_py
from cputh.compile.type_check import run_type_checking
from cputh.utils.utils import check_pyright_installed
from cputh.utils.args import Args
from cputh.utils.flags import DEFAULT_STATE
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
            cputh_code = f.read()
    except UnicodeDecodeError:
        raise CPuthSyntaxError(
            f"cannot read from input: invalid source encoding: '{args.input}'",
            fp=args.input
        )

    py_code, _ = compile_cputh_to_py(cputh_code, DEFAULT_STATE)

    # Syntax checking
    # If the Python is syntactically incorrect, early abort...unless if the
    # user enters the -d or --dangerously flag.
    # Knew we would crash at the speed that we were going; didn't care if the explosion ruined me
    if not args.dangerously_:
        try:
            compile(py_code, args.input.name, mode="exec")
        except SyntaxError as exc:
            raise CPuthSyntaxError(
                msg=str(exc),
                fp=args.input,
                src=cputh_code,
                lineno=exc.lineno - 1 if exc.lineno is not None else None,
            )

    # Write the Python code to the output path
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(py_code)

    # Finally, run type checking on the output
    if not args.dangerously_:
        run_type_checking(py_path=args.output, display_input_path=args.input)

def main(args: Args) -> int:
    try:
        run(args)
        return 0
    except CPuthFileError as exc:
        print(_format_non_runtime_err(exc), file=sys.stderr)
        return 1
    except CPuthTokenError as exc:
        exc.fp = args.input
        print(_format_non_runtime_err(exc), file=sys.stderr)
        return 1
    except CPuthSyntaxError as exc:
        exc.fp = args.input
        print(_format_non_runtime_err(exc), file=sys.stderr)
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
