import sys
from cputh.repl.repl import main as run_repl
from cputh.utils.args import Args

def main(args: Args) -> int:
    exitcode = run_repl()
    return exitcode

if __name__ == "__main__":
    exitcode = main(Args(command=None))
    sys.exit(exitcode)
