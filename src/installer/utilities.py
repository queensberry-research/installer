from __future__ import annotations

from logging import getLogger
from subprocess import PIPE, CalledProcessError, check_call, check_output
from typing import TYPE_CHECKING, Literal, NoReturn, assert_never, overload

if TYPE_CHECKING:
    from pathlib import Path


_LOGGER = getLogger(__name__)


@overload
def run(
    cmd: str,
    /,
    *,
    output: Literal[True],
    cwd: Path | str | None = None,
    failable: Literal[True],
) -> str | None: ...
@overload
def run(
    cmd: str,
    /,
    *,
    output: Literal[True],
    cwd: Path | str | None = None,
    failable: Literal[False] = False,
) -> str: ...
@overload
def run(
    cmd: str,
    /,
    *,
    output: Literal[False] = False,
    cwd: Path | str | None = None,
    failable: bool = False,
) -> None: ...
@overload
def run(
    cmd: str,
    /,
    *,
    output: bool = False,
    cwd: Path | str | None = None,
    failable: bool = False,
) -> str | None: ...
def run(
    cmd: str,
    /,
    *,
    output: bool = False,
    cwd: Path | str | None = None,
    failable: bool = False,
) -> str | None:
    match output:
        case False:
            try:
                _ = check_call(cmd, stdout=PIPE, stderr=PIPE, shell=True, cwd=cwd)
            except CalledProcessError as error:
                if failable:
                    return None
                _run_handle_error(cmd, error)
        case True:
            try:
                return check_output(
                    cmd, stderr=PIPE, shell=True, cwd=cwd, text=True
                ).rstrip("\n")
            except CalledProcessError as error:
                if failable:
                    return None
                _run_handle_error(cmd, error)
        case never:
            assert_never(never)


def _run_handle_error(cmd: str, error: CalledProcessError, /) -> NoReturn:
    lines: list[str] = [f"Error running {cmd!r}"]
    divider = 80 * "-"
    if isinstance(stdout := error.stdout, str) and (stdout != ""):
        lines.extend([divider, "stdout " + 73 * "-", stdout, divider])
    if isinstance(stderr := error.stderr, str) and (stderr != ""):
        lines.extend([divider, "stderr " + 73 * "-", stderr, divider])
    _LOGGER.exception("\n".join(lines))
    raise error


__all__ = ["run"]
