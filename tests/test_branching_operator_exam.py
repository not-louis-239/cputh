#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dist"))

from cputh.compile.compiler import compile_cputh_to_py


EXAM_DIR = ROOT / "tests" / "branching_operator_exam"


class BranchingOperatorExamTests(unittest.TestCase):
    def test_section_a_ok_questions_compile(self) -> None:
        for path in sorted(EXAM_DIR.glob("q*_ok_*.cputh")):
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                compiled = compile_cputh_to_py(source)

                print(f"\033[92mRUNNING TEST: {path}\033[0m")
                print("\033[94mSOURCE:\033[0m")
                print(source)
                print("\033[94mCOMPILED:\033[0m")
                print(compiled)
                compile(compiled, str(path), "exec")

    def test_section_b_bad_questions_fail(self) -> None:
        for path in sorted(EXAM_DIR.glob("q*_bad_*.cputh")):
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")

                print(f"\033[92mRUNNING TEST: {path}\033[0m")
                print("\033[94mSOURCE:\033[0m")
                print(source)

                with self.assertRaises(Exception):
                    compiled = compile_cputh_to_py(source)
                    compile(compiled, str(path), "exec")


if __name__ == "__main__":
    unittest.main()
