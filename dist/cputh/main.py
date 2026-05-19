import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "dist"))

from cputh.repl.repl import run_repl

class Args:
    ...

def parse_args():
    ...

def main():
    run_repl()

if __name__ == "__main__":
    main()
