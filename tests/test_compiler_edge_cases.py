#!/usr/bin/env python3

from __future__ import annotations

import sys
import tokenize
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dist"))

from cputh.compile.compiler import compile_cputh_to_py


class CompileEdgeCaseTests(unittest.TestCase):
    def test_empty_input_compiles_to_empty_python(self) -> None:
        self.assertEqual(compile_cputh_to_py(""), "")

    def test_blank_lines_compile_without_crashing(self) -> None:
        compiled = compile_cputh_to_py("\n\n")
        self.assertEqual(compiled, "\n\n")

    def test_spaces_only_compile_without_crashing(self) -> None:
        compiled = compile_cputh_to_py("    ")
        self.assertEqual(compiled, "    ")

    def test_actual_tab_only_input_does_not_crash(self) -> None:
        compiled = compile_cputh_to_py("\t")
        self.assertEqual(compiled, " ")

    def test_actual_tab_then_name_does_not_crash(self) -> None:
        compiled = compile_cputh_to_py("\teveryone_knows")
        self.assertEqual(compiled, " print")

    def test_backslash_t_only_input_raises_token_error(self) -> None:
        with self.assertRaises(tokenize.TokenError):
            compile_cputh_to_py("\\t")

    def test_backslash_t_then_name_raises_token_error(self) -> None:
        with self.assertRaises(tokenize.TokenError):
            compile_cputh_to_py("\\teveryone_knows")

    def test_increment_rewrite_preserves_indentation(self) -> None:
        compiled = compile_cputh_to_py("    score++\n")
        self.assertEqual(compiled, "    score += 1\n")

    def test_decrement_rewrite_preserves_trailing_comment(self) -> None:
        compiled = compile_cputh_to_py("score-- # encore\n")
        self.assertEqual(compiled, "score -= 1  # encore\n")

    def test_increment_inside_expression_is_not_rewritten(self) -> None:
        with self.assertRaises(SyntaxError):
            compile(compile_cputh_to_py("everyone_knows(score++)\n"), "<test>", "exec")

    def test_unterminated_fstring_currently_raises_token_error(self) -> None:
        with self.assertRaises(tokenize.TokenError):
            compile_cputh_to_py('everyone_knows(f"{TheWayIAm")\n')


if __name__ == "__main__":
    unittest.main()
