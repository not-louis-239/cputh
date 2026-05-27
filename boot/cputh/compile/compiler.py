import io
import re
import tokenize
import token
import random

from cputh.exceptions.errors import CPuthSyntaxError, CPuthTokenError
from cputh.compile.load_gram import load_grammar_file

HEX_CHARS = "0123456789abcdef"

_FSTRING_START = getattr(token, "FSTRING_START", None)
_FSTRING_MIDDLE = getattr(token, "FSTRING_MIDDLE", None)
_FSTRING_END = getattr(token, "FSTRING_END", None)

NESTING_ADD_CHARS = "([{"
NESTING_RM_CHARS = ")]}"

CPUTH_MACRO_KEYWORDS = {
    "sideways", "the_list_goes_on", "perfume_regret", "patient"
}

def _make_hex_salt(length: int) -> str:
    return ''.join(random.choices(HEX_CHARS, k=length))


def _convert_grammar_file_to_flatdict(gfile: dict[str, dict[str, str]]):
    """Convert a dictionary of {cat_name: {cputh_kw: py_kw}}
    to a flat dictionary of {cputh_kw: py_kw}"""

    mapping: dict[str, str] = {}
    for cat_name, cat_contents in gfile.items():
        for cputh, py in cat_contents.items():
            mapping[cputh] = py
    return mapping

CPUTH_MAP = _convert_grammar_file_to_flatdict(load_grammar_file())

# (type, string), e.g. (token.OP, '-')
# the type field can be None
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
    Will only split when nesting is at 0.

    If cannot split, e.g. empty combo tuple or no tokens in LHS
    or RHS, that side will be an empty string."""

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
            if tok.string in NESTING_ADD_CHARS:
                nesting += 1
                i += 1
                continue
            elif tok.string in NESTING_RM_CHARS:
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
        combo_desc = " ".join([s if s is not None else "" for t, s in tok_combo])
        raise CPuthSyntaxError(f"Expected divider sequence sequence '{combo_desc}' not found at nesting root.")

    lhs_tokens = tokens[:split_idx]
    rhs_tokens = tokens[split_idx + combo_len:]

    # HACK: terrible fix, but probably won't look back on it. I spent 2 hours on this one class of bugs and I don't f*cking care anymore
    # Strip out layout-poisoning tokens (NL, NEWLINE, ENDMARKER)
    # This prevents untokenize from panicking and injecting rogue backslashes!
    # F*ck you, untokenize
    lhs_tokens = [t for t in lhs_tokens if t.type not in (token.NL, token.NEWLINE, token.ENDMARKER)]
    rhs_tokens = [t for t in rhs_tokens if t.type not in (token.NL, token.NEWLINE, token.ENDMARKER)]

    # Clean up token position metadata so they sit nicely on row 1
    if lhs_tokens:
        first_row_lhs = lhs_tokens[0].start[0]
        norm_lhs = [t._replace(start=(t.start[0] - first_row_lhs + 1, t.start[1]), end=(t.end[0] - first_row_lhs + 1, t.end[1])) for t in lhs_tokens]
        lhs_str = tokenize.untokenize(norm_lhs).strip()
    else:
        lhs_str = ""

    if rhs_tokens:
        first_row_rhs = rhs_tokens[0].start[0]
        norm_rhs = [t._replace(start=(t.start[0] - first_row_rhs + 1, t.start[1]), end=(t.end[0] - first_row_rhs + 1, t.end[1])) for t in rhs_tokens]
        rhs_str = tokenize.untokenize(norm_rhs).strip()
    else:
        rhs_str = ""

    return lhs_str, rhs_str


class CPuthCompiler:
    def __init__(self) -> None:
        self.inc_dec = re.compile(
            r"^(?P<indent>\s*)(?P<target>.+?)(?P<op>\+\+|--)\s*(?P<comment>#.*)?$"
        )

    def _replace_macro(
            self, idiom_expr: str, full_text: str,
            start_pos: int, end_pos: int
        ) -> str:
        """Convert CPuth destructuring macros directly to Python source."""
        lineno = full_text[:start_pos].count('\n')  # 0-based
        remainder = full_text[end_pos:].lstrip()
        is_statement = remainder.startswith(":")

        # Parse the macro parts out of the idiom_expr substring
        # like "sideways d -< k, v" -> ["sideways d", "k, v"]
        parts = _split_by_tok_combo(idiom_expr, ((token.OP, '-'), (token.OP, '<')))
        left_side, target = parts[0].strip(), parts[1].strip()

        if not target:
            raise CPuthSyntaxError(
                "Expected target variable(s) after destructuring operator", lineno=lineno
            )

        # Token-scan left_side to pinpoint the actual macro keyword
        try:
            tokens = list(tokenize.generate_tokens(io.StringIO(left_side).readline))
            # Strip trailing markers
            while tokens and tokens[-1].type in (token.ENDMARKER, token.NEWLINE):
                tokens.pop()
        except Exception:
            return idiom_expr

        # Find the keyword token (scan backward to respect assignments like 'reader = ')
        keyword_idx = None
        for i in reversed(range(len(tokens))):
            if tokens[i].type == token.NAME and tokens[i].string in CPUTH_MACRO_KEYWORDS:
                keyword_idx = i
                break

        # If no valid CPuth macro keyword is detected at all, drop through to safety
        if keyword_idx is None:
            return idiom_expr

        idiom = tokens[keyword_idx].string

        # Use untokenize to extract the prefix and source expressions completely intact
        prefix = tokenize.untokenize(tokens[:keyword_idx]).strip()
        source = tokenize.untokenize(tokens[keyword_idx + 1:]).strip()

        # Process the idiomatic translation
        translated_expr = ""

        match idiom:
            case "sideways":
                translated_expr = f"for {target} in {source}.items()"

            case "the_list_goes_on":
                translated_expr = f"for {target} in enumerate({source})"

            case "perfume_regret":
                if not is_statement:
                    raise CPuthSyntaxError(
                        "perfume_regret can only be used as a statement block", lineno=lineno
                    )

                if source.startswith('(') and source.endswith(')'):
                    translated_expr = f"with open{source} as {target}"
                else:
                    translated_expr = f"with open({source}) as {target}"

            case "patient":
                sub_parts = _split_by_tok_combo(source, ((None, ","),))

                # Check both parts are non-empty
                if not (sub_parts[0] and sub_parts[1]):
                    raise CPuthSyntaxError("patient expects 'iterable, condition -< name'")

                iterable, cond = sub_parts[0].strip(), sub_parts[1].strip()
                next_expr = f"{target} for {target} in {iterable} if {cond}"
                translated_expr = f"for {target} in ({next_expr})" if is_statement else next_expr

            case bad_kw:
                raise CPuthSyntaxError(f"invalid macro keyword: {bad_kw}")

        # Prepend the original prefix (e.g., "reader = ") to the result
        return f"{prefix} {translated_expr}".strip()

    def _compile_do_until(self, text) -> str:
        """Compile a thats_when_you_said: ... until_it_happens_to_you <cond>
        block to Python code."""

        lines = text.splitlines(keepends=True)
        if not lines:
            return text

        opener = lines[0]
        entry_indent = opener[:len(opener) - len(opener.lstrip())]
        opener_stripped = opener.lstrip()

        # doesn't start with 'thats_when_you_said' -> not a do-until
        if not opener_stripped.startswith("thats_when_you_said:"):
            return text

        closer_idx = None
        for i, line in enumerate(lines[1:], start=1):
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]

            if indent == entry_indent and stripped.startswith("until_it_happens_to_you"):
                closer_idx = i
                break

        if closer_idx is None:
            return text

        body = self._preprocess_do_until_loops("".join(lines[1:closer_idx]))
        condition = lines[closer_idx][len(entry_indent + "until_it_happens_to_you"):].lstrip()

        if closer_idx + 1 < len(lines):
            condition += "".join(lines[closer_idx + 1:])

        condition = condition.rstrip()
        start_var = f"__start_{_make_hex_salt(16)}__"
        condition_expr = condition if condition.startswith("(") and condition.endswith(")") else f"({condition})"

        py_code = (
            f"{entry_indent}{start_var} = [True]\n"
            f"{entry_indent}while ({start_var} and {start_var}.pop()) or not {condition_expr}:\n"
            + body
        )

        return py_code

    def _do_until_condition_is_complete(self, condition: str) -> bool:
        try:
            list(tokenize.generate_tokens(io.StringIO(condition).readline))
        except tokenize.TokenError as exc:
            msg = exc.args[0]

            if "EOF in multi-line" in msg:
                return False

            raise

        return True

    def _preprocess_do_until_loops(self, text) -> str:
        if "thats_when_you_said:" not in text:
            return text

        try:
            lines = text.splitlines(keepends=True)
            tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
        except tokenize.TokenError:
            raise

        stringish_token_types = {
            tokenize.STRING,
            _FSTRING_START,
            _FSTRING_MIDDLE,
            _FSTRING_END,
        }

        string_lines = set()
        for tok in tokens:
            if tok.type in stringish_token_types:
                for lineno in range(tok.start[0] - 1, tok.end[0]):
                    string_lines.add(lineno)

        out: list[str] = []
        i = 0

        while i < len(lines):
            line = lines[i]

            if i in string_lines:
                out.append(line)
                i += 1
                continue

            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]

            # Catch unbegun until loops
            if stripped.startswith("until_it_happens_to_you"):
                raise CPuthSyntaxError(
                    f"Expected 'thats_when_you_said' before 'until_it_happens_to_you' in do-until loop",
                    lineno=i
                )

            if not stripped.startswith("thats_when_you_said:"):
                out.append(line)
                i += 1
                continue

            closer_idx = None
            j = i + 1

            while j < len(lines):
                candidate = lines[j]

                if j in string_lines:
                    j += 1
                    continue

                candidate_stripped = candidate.lstrip()
                candidate_indent = candidate[:len(candidate) - len(candidate_stripped)]

                if candidate_indent == indent and candidate_stripped.startswith("until_it_happens_to_you"):
                    closer_idx = j
                    break

                j += 1

            if closer_idx is None:
                raise CPuthSyntaxError("unterminated do-until loop", lineno=i)

            block_end = closer_idx + 1
            condition = lines[closer_idx][len(indent + "until_it_happens_to_you"):].lstrip()

            while block_end < len(lines) and not self._do_until_condition_is_complete(condition):
                condition += lines[block_end]
                block_end += 1

            block = "".join(lines[i:block_end])
            out.append(self._compile_do_until(block))
            i = block_end

        return "".join(out)

    def _preprocess_destructuring_ops(self, text: str) -> str:
        """Preprocesses destructuring statements (statements containing the
        destructuring operator `-<`) to equivalent Python code.
        Will throw tokenize.TokenErrors if the input text's syntax is malformed."""
        if "-<" not in text:
            return text

        try:
            # Generate character byte offsets for lines to convert row/col to absolute index
            lines = text.splitlines(keepends=True)
            line_offsets = []
            offset = 0
            for l in lines:
                line_offsets.append(offset)
                offset += len(l)

            # Tokenize to identify string/comment literal bounds
            tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
            unsafe_ranges = []
            unsafe_token_types = {
                tokenize.STRING,
                tokenize.COMMENT,
                _FSTRING_START,
                _FSTRING_MIDDLE,
                _FSTRING_END,
            }
            for t in tokens:
                if t.type in unsafe_token_types:
                    start_idx = line_offsets[t.start[0] - 1] + t.start[1]
                    end_idx = line_offsets[t.end[0] - 1] + t.end[1]
                    unsafe_ranges.append((start_idx, end_idx))
        except tokenize.TokenError:
            raise

        # Regex to locate any possible idiom pattern globally (multiline safe)
        # Can match across lines, but stops instantly if it hits an empty line (\n\n) or comment start (#)
        macro_pattern = re.compile(
            r'\b(sideways|the_list_goes_on|perfume_regret|patient)\s+(?:(?!\n\n)[^#])*?-<.*?(?=[:\n)}\]])',
            re.DOTALL
        )

        # Process from right to left to maintain valid string offsets during mutations
        out = text
        matches = list(macro_pattern.finditer(text))

        for match in reversed(matches):
            start, end = match.start(), match.end()

            # Check if this match overlaps with any tokenized string/comment boundaries
            is_inside_literal = False
            for u_start, u_end in unsafe_ranges:
                if u_start <= start < u_end:
                    is_inside_literal = True
                    break

            if is_inside_literal:
                continue

            # Slice and convert
            idiom_expr = match.group(0)
            replacement = self._replace_macro(idiom_expr, out, start, end)
            out = out[:start] + replacement + out[end:]

        return out

    def _rewrite_increment_decrement_lines(self, text: str) -> str:
        """Rewrite lines that use the increment (++) or decrement (--)
        operators to their equivalent += 1 or -= 1 forms.
        This is a pre-processing step before tokenization, since the Python
        tokenizer doesn't understand ++ or -- as valid operators."""

        try:
            tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
        except tokenize.TokenError:
            raise

        lines = text.splitlines(keepends=True)
        line_offsets = []
        offset = 0
        for line in lines:
            line_offsets.append(offset)
            offset += len(line)

        unsafe_ranges = []
        unsafe_token_types = {
            tokenize.STRING,
            tokenize.COMMENT,
            _FSTRING_START,
            _FSTRING_MIDDLE,
            _FSTRING_END,
        }
        for tok in tokens:
            if tok.type in unsafe_token_types:
                start_idx = line_offsets[tok.start[0] - 1] + tok.start[1]
                end_idx = line_offsets[tok.end[0] - 1] + tok.end[1]
                unsafe_ranges.append((start_idx, end_idx))

        op_pattern = re.compile(r"(?P<target>[^;\n]+?)(?P<op>\+\+|--)(?P<suffix>\s*)$")
        out: list[str] = []

        for line_idx, line in enumerate(lines):
            newline = ""
            body = line

            if body.endswith("\r\n"):
                newline = "\r\n"
                body = body[:-2]
            elif body.endswith("\n"):
                newline = "\n"
                body = body[:-1]

            comment_idx = body.find("#")
            code_part = body[:comment_idx] if comment_idx != -1 else body
            comment = body[comment_idx:] if comment_idx != -1 else ""

            segments = code_part.split(";")
            new_segments: list[str] = []
            segment_cursor = line_offsets[line_idx]

            for idx, segment in enumerate(segments):
                segment_text = segment
                segment_abs_end = segment_cursor + len(segment_text)

                is_unsafe = False
                for unsafe_start, unsafe_end in unsafe_ranges:
                    if unsafe_start < segment_abs_end and segment_cursor < unsafe_end:
                        is_unsafe = True
                        break

                if not is_unsafe:
                    match = op_pattern.search(segment_text)

                    if match:
                        target = match.group("target").rstrip()
                        op = match.group("op")
                        suffix = match.group("suffix")
                        assign_op = "+=" if op == "++" else "-="
                        segment_text = f"{target} {assign_op} 1{suffix}"

                new_segments.append(segment_text)
                segment_cursor += len(segment)

                if idx == len(segments) - 1:
                    continue

                segment_cursor += 1

            body = ";".join(new_segments) + comment

            out.append(body + newline)

        return "".join(out)

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
                if tok.string in NESTING_ADD_CHARS:
                    nesting += 1
                    out.append(tok)
                    i += 1
                    continue

                if tok.string in NESTING_RM_CHARS:
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
    """Compile CPuth source to Python.
    Throws CPuthTokenError if tokenisation fails.
    Throws CPuthSyntaxError if parsing fails in another way."""

    compiler = CPuthCompiler()

    try:
        text = compiler._preprocess_do_until_loops(text)
        text = compiler._preprocess_destructuring_ops(text)
        text = compiler._rewrite_increment_decrement_lines(text)
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
        translated, _ = compiler.compile_tokens(tokens, CPUTH_MAP)
        return tokenize.untokenize(translated)

    except tokenize.TokenError as exc:
        raise CPuthTokenError(
            msg=exc.args[0],
            fp=None,  # monkey-patch this with surrounding context by caller if needed: e.fp = input_path
            src=text,
            lineno=exc.args[1][0] - 1,  # -1 to convert lineno to 0-based
        ) from exc
