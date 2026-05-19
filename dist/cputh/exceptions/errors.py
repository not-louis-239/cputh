class CPuthException(Exception):
    def __init__(self, msg: str, fp: Path | None = None) -> None:
        super().__init__(msg)
        self.fp = fp

class CPuthSyntaxError(CPuthException):
    def __init__(
            self, msg: str, fp: Path | None = None,
            src: str | None = None, lineno: int | None = None
        ) -> None:
        super().__init__(msg, fp=fp)
        self.src = src
        self.lineno = lineno

class CPuthTokenError(CPuthSyntaxError):
    pass

class CPuthFileError(CPuthException):
    pass
