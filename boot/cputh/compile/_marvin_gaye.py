import tokenize
import token
import io
from typing import Iterator

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

    def _marvin_gaye_in_src(self, src: str) -> bool:
        """Checks if a standalone `marvin_gaye` is in the CPuth source code
        before a logical statement, ignoring docstrings, comments and whitespace."""
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

            if tok.type == token.NAME and tok.string == "marvin_gaye":
                return True

            return False
        return False

    def preprocess(self, src: str) -> str:
        if not self._marvin_gaye_in_src(src):
            return src

        src_with_thirteens = self._replace_nines_in_src(src)
        lines = src_with_thirteens.splitlines()

        for idx, line in enumerate(lines):
            if line.strip() == "marvin_gaye":
                lines[idx] = ""
                break  # Only remove the top-level trigger

        return "\n".join(lines)
