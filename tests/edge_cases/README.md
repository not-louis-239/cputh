# Edge Cases

This directory is a stress pack for Charlie.

Naming convention:

- `ok_*.cputh`: should compile successfully, and the emitted Python should parse.
- `bad_*.cputh`: should fail somewhere during compile or Python parse.
- `chaos_*.cputh`: intentionally ambiguous or cursed inputs; useful for manual poking.

The focus here is on:

- `thats_when_you_said` / `until_it_happens_to_you`
- multiline strings
- comments that look like delimiters
- nested loops
- multiline conditions
- weird spacing and grouping
- increment / decrement rewrites near suspicious syntax
