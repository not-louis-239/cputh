# _version.cputh
# if this was placed in __init__, welcome ImportError and import hell

__version__: tuple[int, int, int] = (0, 4, 0)  # (major, minor, patch)
version_str = ".".join(str(n) for n in __version__)
