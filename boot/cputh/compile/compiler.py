import io
import re
import tokenize
import token

from cputh.exceptions.errors import CPuthSyntaxError, CPuthTokenError
from cputh.compile.load_gram import load_grammar_file

_FSTRING_START = getattr(token, "FSTRING_START", None)
_FSTRING_MIDDLE = getattr(token, "FSTRING_MIDDLE", None)
_FSTRING_END = getattr(token, "FSTRING_END", None)

def _convert_grammar_file_to_flatdict(gfile: dict[str, dict[str, str]]):
    """Convert a dictionary of {cat_name: {cputh_kw: py_kw}}
    to a flat dictionary of {cputh_kw: py_kw}"""

    mapping: dict[str, str] = {}
    for cat_name, cat_contents in gfile.items():
        for cputh, py in cat_contents.items():
            mapping[cputh] = py
    return mapping

CPUTH_MAP = _convert_grammar_file_to_flatdict(load_grammar_file())
_INC_DEC_STMT = re.compile(r"^(?P<indent>\s*)(?P<target>.+?)(?P<op>\+\+|--)\s*(?P<comment>#.*)?$")

def _rewrite_increment_decrement_lines(text: str) -> str:
    """Rewrite lines that use the increment (++) or decrement (--)
    operators to their equivalent += 1 or -= 1 forms.
    This is a pre-processing step before tokenization, since the Python
    tokenizer doesn't understand ++ or -- as valid operators."""

    out: list[str] = []

    for line in text.splitlines(keepends=True):
        newline = ""
        body = line

        if body.endswith("\r\n"):
            newline = "\r\n"
            body = body[:-2]
        elif body.endswith("\n"):
            newline = "\n"
            body = body[:-1]

        match = _INC_DEC_STMT.fullmatch(body)
        if match:
            indent = match.group("indent")
            target = match.group("target").rstrip()
            op = match.group("op")
            comment_match = match.group("comment")
            comment = comment_match if comment_match else ""

            if op == "++":
                body = f"{indent}{target} += 1"
            else:
                body = f"{indent}{target} -= 1"

            if comment:
                body += f"  {comment}"

        out.append(body + newline)

    return "".join(out)

class CPuthCompiler:
    def _compile_name_token(self, tok: tokenize.TokenInfo, cputh_map: dict[str, str]) -> tokenize.TokenInfo:
        if tok.type != token.NAME:
            return tok
        return tok._replace(string=cputh_map.get(tok.string, tok.string))

    def _compile_fstring(
            self,
            tokens: list[tokenize.TokenInfo],
            cputh_map: dict[str, str],
            start: int,
        ) -> tuple[list[tokenize.TokenInfo], int]:
        out = [tokens[start]]
        i = start + 1

        while i < len(tokens):
            tok = tokens[i]

            if tok.type == _FSTRING_MIDDLE:
                out.append(tok)
                i += 1
                continue

            if tok.type == token.OP and tok.string == "{":
                field_tokens, i = self._compile_replacement_field(tokens, cputh_map, i)
                out.extend(field_tokens)
                continue

            if tok.type == _FSTRING_END:
                out.append(tok)
                return out, i + 1

            out.append(self._compile_name_token(tok, cputh_map))
            i += 1

        raise CPuthSyntaxError("unterminated f-string")

    def _compile_replacement_field(
            self,
            tokens: list[tokenize.TokenInfo],
            cputh_map: dict[str, str],
            start: int,
        ) -> tuple[list[tokenize.TokenInfo], int]:
        out = [tokens[start]]
        i = start + 1
        nesting = 0

        while i < len(tokens):
            tok = tokens[i]

            if tok.type == _FSTRING_START:
                nested_fstring, i = self._compile_fstring(tokens, cputh_map, i)
                out.extend(nested_fstring)
                continue

            if tok.type == token.OP:
                if tok.string in "([{":
                    nesting += 1
                    out.append(tok)
                    i += 1
                    continue

                if tok.string in ")]}":
                    if tok.string == "}" and nesting == 0:
                        out.append(tok)
                        return out, i + 1

                    nesting -= 1
                    out.append(tok)
                    i += 1
                    continue

                if nesting == 0 and tok.string == "=":
                    out.append(tok)
                    return self._compile_replacement_field_tail(tokens, cputh_map, out, i + 1)

                if nesting == 0 and tok.string == "!":
                    out.append(tok)
                    i += 1
                    if i < len(tokens):
                        out.append(tokens[i])
                        i += 1
                    return self._compile_format_spec(tokens, cputh_map, out, i)

                if nesting == 0 and tok.string == ":":
                    out.append(tok)
                    return self._compile_format_spec(tokens, cputh_map, out, i + 1)

            out.append(self._compile_name_token(tok, cputh_map))
            i += 1

        raise CPuthSyntaxError("unterminated f-string replacement field")

    def _compile_replacement_field_tail(
            self,
            tokens: list[tokenize.TokenInfo],
            cputh_map: dict[str, str],
            out: list[tokenize.TokenInfo],
            start: int,
        ) -> tuple[list[tokenize.TokenInfo], int]:
        i = start

        if i < len(tokens) and tokens[i].type == token.OP and tokens[i].string == "!":
            out.append(tokens[i])
            i += 1
            if i < len(tokens):
                out.append(tokens[i])
                i += 1

        if i < len(tokens) and tokens[i].type == token.OP and tokens[i].string == ":":
            out.append(tokens[i])
            return self._compile_format_spec(tokens, cputh_map, out, i + 1)

        if i < len(tokens) and tokens[i].type == token.OP and tokens[i].string == "}":
            out.append(tokens[i])
            return out, i + 1

        raise CPuthSyntaxError("invalid f-string replacement field")

    def _compile_format_spec(
            self,
            tokens: list[tokenize.TokenInfo],
            cputh_map: dict[str, str],
            out: list[tokenize.TokenInfo],
            start: int,
        ) -> tuple[list[tokenize.TokenInfo], int]:
        i = start

        while i < len(tokens):
            tok = tokens[i]

            if tok.type == _FSTRING_MIDDLE:
                out.append(tok)
                i += 1
                continue

            if tok.type == token.OP and tok.string == "{":
                nested_field, i = self._compile_replacement_field(tokens, cputh_map, i)
                out.extend(nested_field)
                continue

            if tok.type == token.OP and tok.string == "}":
                out.append(tok)
                return out, i + 1

            out.append(self._compile_name_token(tok, cputh_map))
            i += 1

        raise CPuthSyntaxError("unterminated f-string format specifier")

    def compile_tokens(
            self,
            tokens: list[tokenize.TokenInfo],
            cputh_map: dict[str, str],
            start: int = 0,
        ) -> tuple[list[tokenize.TokenInfo], int]:
        out: list[tokenize.TokenInfo] = []
        i = start

        while i < len(tokens):
            tok = tokens[i]

            if tok.type == _FSTRING_START:
                fstring_tokens, i = self._compile_fstring(tokens, cputh_map, i)
                out.extend(fstring_tokens)
                continue

            out.append(self._compile_name_token(tok, cputh_map))
            i += 1

        return out, i

def compile_cputh_to_py(text: str) -> str:
    """Compile CPuth source to Python. Throws CPuthTokenError if tokenisation fails."""

    try:
        text = _rewrite_increment_decrement_lines(text)
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
        translated, _ = CPuthCompiler().compile_tokens(tokens, CPUTH_MAP)
        return tokenize.untokenize(translated)
    except tokenize.TokenError as exc:
        raise CPuthTokenError(
            msg=exc.args[0],
            fp=None,  # monkey-patch this with surrounding context by caller if needed: e.fp = input_path
            src=text,
            lineno=exc.args[1][0] - 1,  # -1 to convert lineno to 0-based
        ) from exc
