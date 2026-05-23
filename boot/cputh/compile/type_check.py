import subprocess
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from cputh.utils.utils import check_pyright_installed
from cputh.utils.format_tools import (
    COL_BOLD,
    COL_ERR,
    COL_WARN,
    COL_RESET
)

@dataclass(frozen=True)
class DiagnosticOutputLine:
    lineno: int
    msg: str
    severity: str  # "error", "warning", "information"

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

def run_type_checking(py_path: Path, display_input_path: Path) -> None:
    """
    Run Pyright on the given Python file and print formatted diagnostics to stderr.

    py_path            = path to the compiled Python output
    display_input_path = the input source file that Charlie 'blames' when there are errors
    """

    # If Pyright not installed, can't do type checking
    if not check_pyright_installed():
        print(
            f"{COL_WARN}{COL_BOLD}save your apologies {COL_RESET}{COL_WARN}(skipping type checking: pyright not installed - how long has this been going on?){COL_RESET}",
            file=sys.stderr
        )
        return

    proc = subprocess.run(
        ["pyright", "--outputjson", py_path],
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

    # If no diagnostic output, early return
    if not diag_output:
        return

    # Print summary of Pyright output
    print(f"{COL_WARN}{COL_BOLD}you just want attention {COL_RESET}{COL_WARN}(static analysis warnings, file: '{display_input_path}'):{COL_RESET}", file=sys.stderr)
    print(
        f"{num_errors} error{"s" if num_errors != 1 else ""}"
        f", {num_warnings} warning{"s" if num_warnings != 1 else ""}"
        f", {num_infos} information{"s" if num_infos != 1 else ""}",
        file=sys.stderr
    )

    for line in diag_output:
        severity_col = COL_ERR if line.severity == "error" else COL_WARN
        print(
            f"{severity_col}{COL_BOLD}{line.severity}{COL_RESET}: "
            f"line {line.lineno}: {line.msg}",
            file=sys.stderr
        )
