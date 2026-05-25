import sys
import os
import argparse
from pathlib import Path
from typing import Literal
from dataclasses import dataclass

if (bootstrap := Path(__file__).parents[2] / "boot").exists():
    sys.path.insert(0, str(bootstrap))
elif (distribution := Path(__file__).parents[2] / "dist").exists():
    sys.path.insert(0, str(distribution))
else:
    raise RuntimeError("Could not find distribution or bootstrap directory. We don't talk anymore.")

from cputh.utils.args import parse_args, Args

def main() -> None:
    args = parse_args()

    match args.command:
        case "compile":
            if args.dir_ is not None:
                os.environ["CPUTH_COMPILE_DIR"] = str(args.dir_)
            from cputh.mains.compile import main as sub_main
        case "sing":
            from cputh.mains.sing import main as sub_main
        case "lyrics":
            from cputh.mains.lyrics import main as sub_main
        case None:
            from cputh.mains.repl import main as sub_main
        case _:
            print(f"Unknown command: {args.command}")
            return 1

    exitcode = sub_main(args)
    sys.exit(exitcode)

if __name__ == "__main__":
    main()
