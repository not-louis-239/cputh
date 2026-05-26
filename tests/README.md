# CPuth Midterm

Welcome to the `tests/` examination hall.

Assessment format:

- `Part A`: direct language feature samples
- `Part B`: fixture packs that stress one subsystem at a time
- `Part C`: cursed material that Charlie may or may not survive

Current papers:

- `branching_op.cputh`: the original worked example for the `-<` branching operator family
- `edge_cases/`: do-until stress pack
- `branching_operator_exam/`: numbered branching-operator edge cases
- `test_compiler_edge_cases.py`: unit-style compiler regressions
- `test_edge_case_fixtures.py`: fixture harness for do-until edge cases
- `test_branching_operator_exam.py`: fixture harness for the branching operator exam

Marking guide:

- `qXX_ok_*.cputh`: should compile successfully, and the emitted Python should parse
- `qXX_bad_*.cputh`: should fail during compile or Python parse
- `qXX_chaos_*.cputh`: currently exposes odd or unstable behavior; kept for investigation
