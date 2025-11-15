from __future__ import annotations

from contextlib import contextmanager
from ipaddress import IPv4Address
from logging import getLogger
from os import environ
from pathlib import Path
from socket import AF_INET, SOCK_DGRAM, socket
from stat import S_IXUSR
from string import Template
from subprocess import PIPE, CalledProcessError, check_call, check_output
from typing import TYPE_CHECKING, Any, Literal, NoReturn, assert_never, overload

from requests import get
from utilities.atomicwrites import writer
from utilities.functools import cache
from utilities.iterables import OneEmptyError, one
from utilities.os import is_pytest
from utilities.tempfile import TemporaryDirectory

from installer.constants import NONROOT
from installer.enums import Subnet
from installer.settings import SETTINGS

if TYPE_CHECKING:
    from collections.abc import Iterator


_LOGGER = getLogger(__name__)


def add_mode(path: Path, mode: int, /) -> None:
    path.chmod(path.stat().st_mode | mode)


def apt_install(pkg: str, /) -> None:
    run(f"apt install {pkg}")


def apt_installed(pkg: str, /) -> bool:
    return run(f"apt list --installed {pkg}") != ""


def apt_update() -> None:
    run("apt update -y")


def is_copied(src: Path | bytes | str, dest: Path, /) -> bool:
    match src:
        case Path():
            return is_copied(src.read_bytes(), dest)
        case bytes():
            return dest.is_file() and (src == dest.read_bytes())
        case str():
            return dest.is_file() and (src == dest.read_text())
        case never:
            assert_never(never)


def copy(src: Path | str, dest: Path, /, **kwargs: Any) -> None:
    match src:
        case Path():
            return copy(src.read_text(), dest, **kwargs)
        case str():
            if len(kwargs) >= 1:
                src = substitute(src, **kwargs)
            if is_pytest():
                return None
            with writer(dest, overwrite=True) as temp_dir:
                _ = temp_dir.write_text(src)
            return None
        case never:
            assert_never(never)


def dpkg_install(path: Path, /) -> None:
    run(f"dpkg -i {path}")


def get_subnet() -> Subnet:
    try:
        return Subnet[environ["SUBNET"]]
    except KeyError:
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.connect(("1.1.1.1", 80))
            ip = IPv4Address(s.getsockname()[0])
        n = int(str(ip).split(".")[2])
        try:
            return one(s for s in Subnet if s.n == n)
        except OneEmptyError:
            msg = f"Invalid IP; got {ip}"
            raise ValueError(msg) from None


def has_non_root() -> bool:
    return run(f"id -u {NONROOT}", failable=True)


@cache
def is_lxc() -> bool:
    try:
        return run("systemd-detect-virt --container", output=True) == "lxc"
    except CalledProcessError:
        return False


@cache
def is_proxmox() -> bool:
    return Path("/etc/pve").is_dir()


@cache
def is_vm() -> bool:
    try:
        return run("systemd-detect-virt --vm", output=True) == "kvm"
    except CalledProcessError:
        return False


@overload
def run(
    cmd: str,
    /,
    *,
    output: Literal[True],
    failable: Literal[True],
    cwd: Path | None = None,
) -> str | None: ...
@overload
def run(
    cmd: str,
    /,
    *,
    output: Literal[True],
    failable: Literal[False] = False,
    cwd: Path | None = None,
) -> str: ...
@overload
def run(
    cmd: str,
    /,
    *,
    output: Literal[False] = False,
    failable: Literal[True],
    cwd: Path | None = None,
) -> bool: ...
@overload
def run(
    cmd: str,
    /,
    *,
    output: Literal[False] = False,
    failable: Literal[False] = False,
    cwd: Path | None = None,
) -> None: ...
@overload
def run(
    cmd: str,
    /,
    *,
    output: bool = False,
    failable: bool = False,
    cwd: Path | None = None,
) -> bool | str | None: ...
def run(
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


def substitute(text: str, /, **kwargs: Any) -> str:
    return Template(text).substitute(**kwargs)


def touch(path: Path, /) -> None:
    if is_pytest():
        return
    path.touch()


@contextmanager
def yield_github_download(owner: str, repo: str, filename: str, /) -> Iterator[Path]:
    releases = f"{owner}/{repo}/releases"
    url1 = f"https://api.github.com/repos/{releases}/latest"
    resp1 = get(url1, timeout=SETTINGS.downloads.timeout)
    resp1.raise_for_status()
    tag = resp1.json()["tag_name"]
    filename_use = substitute(filename, tag=tag, tag_without=tag.lstrip("v"))
    url2 = f"https://github.com/{releases}/download/{tag}/{filename_use}"
    with get(url2, timeout=SETTINGS.downloads.timeout, stream=True) as resp2:
        resp2.raise_for_status()
        with TemporaryDirectory() as temp_dir:
            temp_file = temp_dir / filename_use
            with temp_file.open("wb") as fh:
                for chunk in resp2.iter_content(
                    chunk_size=SETTINGS.downloads.chunk_size
                ):
                    if chunk:
                        _ = fh.write(chunk)
            add_mode(temp_file, S_IXUSR)
            yield temp_file


__all__ = [
    "add_mode",
    "apt_install",
    "apt_installed",
    "apt_update",
    "copy",
    "dpkg_install",
    "get_subnet",
    "has_non_root",
    "is_copied",
    "is_lxc",
    "is_proxmox",
    "is_vm",
    "run",
    "substitute",
    "touch",
    "yield_github_download",
]
