__version__: tuple[int, int, int] = (0, 3, 1)  # (major, minor, patch)

def make_version_str() -> str:
    return ".".join(str(n) for n in __version__)
