# Copyright 2026 Louis Masarei-Boulton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Charlie Puth-flavoured exception objects for the REPL, compiler and
direct interpreter (`cputh sing`).

Thrown for:
* file errors in the compiler or direct interpreter, e.g. src file doesn't exist
* token errors in the compiler, direct interpreter or REPL (a layer of abstraction above `tokenize.TokenError`)
* syntax errors in the compiler or direct interpreter

Should NOT cover Python-side syntax errors in the REPL or direct interpreter.
This is because in the REPL, Python-side syntax errors come from
malformed code after it has already been tokenised. Hence they remain distinct.
"""

from pathlib import Path

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
