from pathlib import Path
import json

GRAMMAR_FILE_PATH: Path = Path(__file__).parents[3] / "data" / "cputh.gram.json"

def parse_grammar_file(contents: str) -> dict[str, dict[str, str]]:
    """Parse the grammar file contents and return a dictionary of {category_name: {cputh_kw: py_kw}}.
     If parsing fails or the expected structure is not found, throws a RuntimeError."""

    gram = json.loads(contents).get("cputh_grammar")
    if gram is None:
        raise RuntimeError("Could not load Charlie Puth grammar file. We don't talk anymore.")
    return gram

def load_grammar_file() -> dict[str, dict[str, str]]:
    with open(GRAMMAR_FILE_PATH, "r", encoding="utf-8") as f:
        contents: str = f.read()
        return parse_grammar_file(contents)

def _test():
    gram: dict[str, dict[str, str]] = load_grammar_file()
    print(gram)

if __name__ == "__main__":
    _test()
