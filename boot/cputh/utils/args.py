from typing import Literal
from dataclasses import dataclass, field
from pathlib import Path
import argparse

@dataclass
class Args:
    command: Literal["compile", "sing", "lyrics", None]
    input: Path | None = None                  # compile + sing
    output: Path | None = None                            # compile + sing
    dir_: Path | None = None                              # compile only
    force: bool = False                              # compile only
    dangerously_: bool = False                       # compile only
    trailing_args: list[str] = field(default_factory=list)  # sing only

def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        prog="cputh",
        description="Compile Charlie Puth code to Python. Why use boring keywords when your source can have feelings?"
    )
    parser.add_argument(
        "--dir",
        type=Path,
        dest="dir_",
        help="force the compiler to reference this directory when loading itself instead of its default import location"
    )
    subparsers = parser.add_subparsers(dest="command")

    # compile
    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("input", type=Path, help="path to the input .cputh file")
    compile_parser.add_argument("-o", "--output", type=Path, required=True, help="path to the output .py file")
    compile_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="overwrite the output file if it already exists"
    )
    compile_parser.add_argument(
        "-d", "--dangerously",
        action="store_true",
        dest="dangerously_",  # attribute name in which to store the attr, trailing underscore avoids keyword collision
        help="skip syntax and type checking. (I knew we would crash at the speed that we were going)"
    )

    # sing
    sing_parser = subparsers.add_parser("sing")
    sing_parser.add_argument("input", type=Path, help="path to the .cputh file to execute directly")
    sing_parser.add_argument("-o", "--output", type=Path, required=False, help="produce a Python compiled file at this file path if provided")

    # lyrics
    lyrics_parser = subparsers.add_parser("lyrics")

    args_raw = parser.parse_args()

    return Args(
        command=args_raw.command,
        input=getattr(args_raw, "input", None),
        output=getattr(args_raw, "output", None),
        dir_=getattr(args_raw, "dir_", None),
        force=getattr(args_raw, "force", False),
        dangerously_=getattr(args_raw, "dangerously_", False),
    )
