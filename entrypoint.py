#!/usr/bin/env python3
from __future__ import annotations

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from dataclasses import dataclass
from logging import basicConfig, getLogger
from os import getuid
from pathlib import Path
from shutil import which
from socket import gethostname
from subprocess import PIPE, CalledProcessError, check_call, check_output
from typing import Any, Literal, NoReturn, Self, assert_never, overload

# THIS MODULE CANNOT CONTAIN ANY THIRD PARTY IMPORTS


_FORMAT = (
    f"[{{asctime}} ❯ {gethostname()} ❯ {{module}}:{{funcName}}:{{lineno}}] {{message}}"  # noqa: RUF001
)
basicConfig(format=_FORMAT, datefmt="%Y-%m-%d %H:%M:%S", style="{", level="INFO")
_LOGGER = getLogger(__name__)
_IS_ROOT = getuid() == 0
_SUDO = "" if _IS_ROOT else "sudo "
_REPO_URL = "https://github.com/dycw/test-remote-script.git"
_REPO_PATH = Path("/tmp/installer")  # noqa: S108
__version__ = "0.1.9"


def _main() -> None:
    _LOGGER.info("Running entrypoint %s...", __version__)
    settings, args = _Settings.parse()
    _ensure_repo_cloned(settings.url, settings.path)
    _ensure_repo_version(settings.path, version=settings.version)
    _install_uv()
    cmd = " ".join(["uv run python3 -m installer.main", *args])
    _LOGGER.info("Running: %r", cmd)
    _ = check_call(cmd, shell=True, cwd=settings.path)


@dataclass(order=True, unsafe_hash=True, kw_only=True, slots=True)
class _Settings:
    url: str = _REPO_URL
    path: Path = _REPO_PATH
    version: str | None = None

    @classmethod
    def parse(cls) -> tuple[Self, Any]:
        parser = ArgumentParser(
            formatter_class=ArgumentDefaultsHelpFormatter,
            add_help=False,
            suggest_on_error=True,
        )
        _ = parser.add_argument(
            "--repo-url", type=str, default=_REPO_URL, help="Repo URL", dest="url"
        )
        _ = parser.add_argument(
            "--repo-path", type=Path, default=_REPO_PATH, help="Repo path", dest="path"
        )
        _ = parser.add_argument(
            "--repo-version",
            type=str,
            default=None,
            help="Repo version",
            dest="version",
        )
        namespace, args = parser.parse_known_args()
        settings = cls(**vars(namespace))
        return settings, args


def _ensure_apt_installed(cmd: str, /) -> None:
    if which(cmd) is not None:
        return
    _LOGGER.info("Updating 'apt'...")
    _run(f"{_SUDO} apt update -y")
    _LOGGER.info("Installing %r...", cmd)
    _run(f"{_SUDO} apt install -y {cmd}")


def _ensure_repo_cloned(url: str, path: Path, /) -> None:
    if path.is_dir():
        return
    _ensure_apt_installed("git")
    _LOGGER.info("Cloning %r to %r...", url, str(path))
    _run(f"git clone {url} {path}")


def _ensure_repo_version(path: Path, /, *, version: str | None = None) -> None:
    if version is None:
        return
    tag = _run(
        "git describe --tags --exact-match", output=True, failable=True, cwd=path
    )
    if tag is None:
        current = _run("git rev-parse --abbrev-ref HEAD", output=True, cwd=path)
    else:
        current = tag
    if current == version:
        _LOGGER.info("Pulling %r on %r...", str(path), current)
        try:
            _run("git pull", cwd=path)
        except CalledProcessError:
            _run("git checkout master", cwd=path)
            _run("git pull", cwd=path)
            _run(f"git branch -D {current}", cwd=path)
            _run(f"git checkout {version}", cwd=path)
        return
    _LOGGER.info("We got curr = %r, ver = %r", current, version)
    _LOGGER.info("Switching %r to %r...", str(path), version)
    _run(f"git checkout {version}", cwd=path)


def _install_uv() -> None:
    if which("uv") is not None:
        return
    _ensure_apt_installed("curl")
    _LOGGER.info("Installing 'uv'...")
    url = "https://astral.sh/uv/install.sh"
    path = Path("/usr/local/bin")
    _run(f"curl -LsSf {url} | env UV_INSTALL_DIR={path} UV_NO_MODIFY_PATH=1 sh")
    _run(f"chmod +x {path}/{{uv, uvx}}")


@overload
def _run(
    cmd: str,
    /,
    *,
    output: Literal[True],
    failable: Literal[True],
    cwd: Path | None = None,
) -> str | None: ...
@overload
def _run(
    cmd: str,
    /,
    *,
    output: Literal[True],
    failable: Literal[False] = False,
    cwd: Path | None = None,
) -> str: ...
@overload
def _run(
    cmd: str,
    /,
    *,
    output: Literal[False] = False,
    failable: Literal[True],
    cwd: Path | None = None,
) -> bool: ...
@overload
def _run(
    cmd: str,
    /,
    *,
    output: Literal[False] = False,
    failable: Literal[False] = False,
    cwd: Path | None = None,
) -> None: ...
@overload
def _run(
    cmd: str,
    /,
    *,
    output: bool = False,
    failable: bool = False,
    cwd: Path | None = None,
) -> bool | str | None: ...
def _run(
    cmd: str,
    /,
    *,
    output: bool = False,
    failable: bool = False,
    cwd: Path | None = None,
) -> bool | str | None:
    match output, failable:
        case False, False:
            try:
                _run_check_call(cmd, cwd=cwd)
            except CalledProcessError as error:
                _run_handle_error(cmd, error)
        case False, True:
            try:
                _run_check_call(cmd, cwd=cwd)
            except CalledProcessError:
                return False
            return True
        case True, False:
            try:
                return _run_check_output(cmd, cwd=cwd)
            except CalledProcessError as error:
                _run_handle_error(cmd, error)
        case True, True:
            try:
                return _run_check_output(cmd, cwd=cwd)
            except CalledProcessError:
                return None
        case never:
            assert_never(never)


def _run_check_call(cmd: str, /, *, cwd: Path | None = None) -> None:
    _ = check_call(cmd, stdout=PIPE, stderr=PIPE, shell=True, cwd=cwd)


def _run_check_output(cmd: str, /, *, cwd: Path | None = None) -> str:
    return check_output(cmd, stderr=PIPE, shell=True, cwd=cwd, text=True).rstrip("\n")


def _run_handle_error(cmd: str, error: CalledProcessError, /) -> NoReturn:
    lines: list[str] = [f"Error running {cmd!r}"]
    divider = 80 * "-"
    if isinstance(stdout := error.stdout, str) and (stdout != ""):
        lines.extend([divider, "stdout " + 73 * "-", stdout, divider])
    if isinstance(stderr := error.stderr, str) and (stderr != ""):
        lines.extend([divider, "stderr " + 73 * "-", stderr, divider])
    _LOGGER.exception("\n".join(lines))
    raise error


if __name__ == "__main__":
    _main()
