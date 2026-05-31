import tokenize
import token
import io
from typing import Iterator
from cputh.utils.flags import F_MARVIN_GAYE, DEFAULT_STATE, flag_is_active, add_flag

def kw_is_in_src(src: str, *, kw: str) -> bool:
    """Checks if a standalone specific keyword is in the CPuth source code
    before a logical statemnt, ignoring docstrings, comments and whitepsace."""
    try:
        tokens: Iterator[tokenize.TokenInfo] = tokenize.generate_tokens(io.StringIO(src).readline)
    except tokenize.TokenError:
        # Fallback if the source code contains unclosed strings/brackets
        return False

    for tok in tokens:
        if tok.type in (token.NL, token.NEWLINE, tokenize.COMMENT, token.INDENT, token.DEDENT):
            continue
        if tok.type == token.STRING:
            continue

        if tok.type == token.NAME and tok.string == kw:
            return True

        return False
    return False

class _MarvinGaye:
    def _replace_nines_in_src(self, src: str) -> str:
        """Replace all integer literals with a value of 9 in the source
        stream with 13s."""

        toks: list[tokenize.TokenInfo] = list(tokenize.generate_tokens(io.StringIO(src).readline))

        # TokenInfo objects are immutable so we have to overwrite indices
        for idx, tok in enumerate(toks):
            if tok.type == token.NUMBER and tok.string == "9":
                toks[idx] = tok._replace(string="13")

        return tokenize.untokenize(toks)

    def preprocess(self, src: str, init_flags: int) -> tuple[str, int]:
        """Returns (modified source, init flags | any new flags discovered)"""
        mg_active = kw_is_in_src(src, kw="marvin_gaye") or flag_is_active(init_flags, f=F_MARVIN_GAYE)

        if not mg_active:
            return (src, init_flags)

        src_with_thirteens = self._replace_nines_in_src(src)
        lines = src_with_thirteens.splitlines()
        flags = add_flag(init_flags, f=F_MARVIN_GAYE)

        for idx, line in enumerate(lines):
            # Blank out the flag line so it doesn't crash the interpreter with a syntax error
            # Only remove the top-level trigger
            if line.strip() == "marvin_gaye":
                lines[idx] = ""
                break

        return ("\n".join(lines), flags)
