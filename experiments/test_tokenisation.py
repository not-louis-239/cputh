# test to compile just the first part of a `patient` idiom

from typing import TypeAlias
import tokenize
import token
import io

NESTING_ADD_TOKENS = "([{"
NESTING_RM_TOKENS = ")]}"

# (type, string), e.g. (token.OP, '-')
# either (but not both) fields can be None
# None fields match any value
_TokenSpecifier = tuple[int | None, str]

def _tok_matches(tok: tokenize.TokenInfo, spec: _TokenSpecifier) -> bool:
    spec_typ, spec_string = spec
    return (
        (spec_typ is None or spec_typ == tok.type)
        and
        (spec_string == tok.string)
    )

def _split_by_tok_combo(
        text: str, tok_combo: tuple[_TokenSpecifier, ...]
    ) -> tuple[str, str]:
    """Split source text by the first appearance of an ordered
    combination of tokens of any length. Returns (LHS, RHS).
    Will only split when nesting is at 0."""

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except tokenize.TokenError as e:
        raise

    # Remove trailing layout tokens so untokenize doesn't introduce syntax bloat
    while tokens and tokens[-1].type in (token.ENDMARKER, token.NEWLINE):
        tokens.pop()

    combo_len = len(tok_combo)
    if combo_len == 0:
        return text, ""

    split_idx = None
    nesting = 0
    i = 0

    # Scan with a sliding window large enough to fit the combination
    while i <= len(tokens) - combo_len:
        tok = tokens[i]

        # Manage nesting boundaries using OP matching rules
        if tok.type == token.OP:
            if tok.string in NESTING_ADD_TOKENS:
                nesting += 1
                i += 1
                continue
            elif tok.string in NESTING_RM_TOKENS:
                nesting -= 1
                i += 1
                continue

        # Look for the sequential combo pattern only outside of blocks/brackets
        if nesting == 0:
            match_found = True
            for offset in range(combo_len):
                if not _tok_matches(tokens[i + offset], tok_combo[offset]):
                    match_found = False
                    break

            if match_found:
                split_idx = i
                break

        i += 1

    if split_idx is None:
        # Generate a descriptive error if the sequence sequence can't be matched
        combo_desc = " ".join([s or f"Type({t})" for t, s in tok_combo])
        raise SyntaxError(f"Expected divider sequence sequence '{combo_desc}' not found at nesting root.")

    # Slice tokens around the located delimiter window
    lhs_tokens = tokens[:split_idx]
    rhs_tokens = tokens[split_idx + combo_len:]

    # Regenerate raw source code layout
    lhs_str = tokenize.untokenize(lhs_tokens).strip() if lhs_tokens else ""
    rhs_str = tokenize.untokenize(rhs_tokens).strip() if rhs_tokens else ""

    return lhs_str, rhs_str

test = "patient [track, \"decoy\"], len(x) > 0 -< x"
lhs, rhs = _split_by_tok_combo(test, ((token.OP, '-'), (token.OP, '<')))
iter_, cond = _split_by_tok_combo(lhs, ((None, ","),))
print(iter_)
print(cond)
print(rhs)

final_py_code = f"{rhs} for {rhs} in {iter_} if {cond}"
print(final_py_code)