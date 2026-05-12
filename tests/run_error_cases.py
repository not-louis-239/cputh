#!/usr/bin/env python3

from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPILER_PATH = ROOT / "src" / "compiler" / "compiler.py"
BIN_PATH = ROOT / "bin" / "cputh"

COL_FAINT = "\033[2m"
COL_RESET = "\033[0m"
EMPTY_SENTINEL_DISPLAY = F"{COL_FAINT}<empty>{COL_RESET}"

def load_compiler_module():
    spec = importlib.util.spec_from_file_location("cputh_compiler_for_tests", COMPILER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load compiler module from {COMPILER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cli_case(name: str, input_path: Path, output_path: Path) -> dict[str, object]:
    proc = subprocess.run(
        [str(BIN_PATH), str(input_path), str(output_path)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    return {
        "case": name,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def run_module_case(name: str, patcher) -> dict[str, object]:
    compiler = load_compiler_module()
    stdout = io.StringIO()
    stderr = io.StringIO()

    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        undo = patcher(compiler)
        try:
            exit_code = compiler.main()
        finally:
            undo()

    return {
        "case": name,
        "exit_code": exit_code,
        "stdout": stdout.getvalue(),
        "stderr": stderr.getvalue(),
    }


def patch_attr(obj, name: str, replacement):
    original = getattr(obj, name)
    setattr(obj, name, replacement)

    def undo():
        setattr(obj, name, original)

    return undo


def main() -> int:
    results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="cputh-errors-") as tmpdir:
        tmp = Path(tmpdir)
        existing_output = tmp / "existing.py"
        existing_output.write_text("# already here\n", encoding="utf-8")

        valid_input = tmp / "valid.cputh"
        valid_input.write_text('everyone_knows("hi")\n', encoding="utf-8")

        token_error_input = tmp / "token_error.cputh"
        token_error_input.write_text('everyone_knows("""oops)\n', encoding="utf-8")

        syntax_error_input = tmp / "syntax_error.cputh"
        syntax_error_input.write_text('attention TheWayIAm\n    everyone_knows("oops")\n', encoding="utf-8")

        type_error_input = tmp / "type_error.cputh"
        type_error_input.write_text('x: int = "hello"\n', encoding="utf-8")

        invalid_encoding_input = tmp / "invalid_encoding.cputh"
        invalid_encoding_input.write_bytes(b"\xff\xfe\x00bad")

        not_a_file = tmp / "not_a_file"
        not_a_file.mkdir()

        results.append(run_cli_case("missing input file", tmp / "READNE.md", tmp / "out.py"))
        results.append(run_cli_case("input path is directory", not_a_file, tmp / "out.py"))
        results.append(run_cli_case("missing output parent", valid_input, tmp / "missing-dir" / "out.py"))
        results.append(run_cli_case("output already exists", valid_input, existing_output))
        results.append(run_cli_case("invalid source encoding", invalid_encoding_input, tmp / "invalid_encoding.py"))
        results.append(run_cli_case("token error", token_error_input, tmp / "token_error.py"))
        results.append(run_cli_case("syntax error", syntax_error_input, tmp / "syntax_error.py"))
        results.append(run_cli_case("type checking case", type_error_input, tmp / "type_error.py"))

    def keyboard_interrupt_patcher(compiler):
        def fake_parse_args():
            raise KeyboardInterrupt
        return patch_attr(compiler, "parse_args", fake_parse_args)

    def permission_error_patcher(compiler):
        def fake_parse_args():
            return compiler.Args(Path("in.cputh"), Path("out.py"), False, False)

        def fake_run(_args):
            raise PermissionError("permission test")

        undo_parse = patch_attr(compiler, "parse_args", fake_parse_args)
        undo_run = patch_attr(compiler, "run", fake_run)

        def undo():
            undo_run()
            undo_parse()

        return undo

    def os_error_patcher(compiler):
        def fake_parse_args():
            return compiler.Args(Path("in.cputh"), Path("out.py"), False, False)

        def fake_run(_args):
            raise OSError("os error test")

        undo_parse = patch_attr(compiler, "parse_args", fake_parse_args)
        undo_run = patch_attr(compiler, "run", fake_run)

        def undo():
            undo_run()
            undo_parse()

        return undo

    results.append(run_module_case("keyboard interrupt", keyboard_interrupt_patcher))
    results.append(run_module_case("permission error", permission_error_patcher))
    results.append(run_module_case("os error", os_error_patcher))

    for result in results:
        print(f"CASE: {result['case']}")
        print(f"EXIT: {result['exit_code']}")
        print("STDOUT:")
        stdout = result["stdout"] or EMPTY_SENTINEL_DISPLAY
        print(stdout.rstrip("\n"))
        print("STDERR:")
        stderr = result["stderr"] or EMPTY_SENTINEL_DISPLAY
        print(stderr.rstrip("\n"))
        print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
