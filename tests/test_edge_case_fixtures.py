#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dist"))

from cputh.compile.compiler import compile_cputh_to_py


EDGE_CASE_DIR = ROOT / "tests" / "edge_cases"


class EdgeCaseFixtureTests(unittest.TestCase):
    def test_ok_edge_case_fixtures_compile(self) -> None:
        for path in sorted(EDGE_CASE_DIR.glob("ok_*.cputh")):
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                compiled = compile_cputh_to_py(source)
                print(f"\033[32m --- RUNNING TEST: {path} --- \033[0m")
                print(f"\033[34m --- SOURCE: {path} --- \033[0m")
                print(source)
                compiled = compile_cputh_to_py(source)
                print(f"\033[34m --- COMPILED: {path} --- \033[0m")
                print(compiled)
                compile(compiled, str(path), "exec")

    def test_bad_edge_case_fixtures_fail_somewhere(self) -> None:
        for path in sorted(EDGE_CASE_DIR.glob("bad_*.cputh")):
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")

                with self.assertRaises(Exception):
                    compiled = compile_cputh_to_py(source)
                    compile(compiled, str(path), "exec")


if __name__ == "__main__":
    unittest.main()
