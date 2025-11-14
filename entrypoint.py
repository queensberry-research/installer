#!/usr/bin/env python3
from __future__ import annotations

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from dataclasses import dataclass
from logging import basicConfig, getLogger
from os import getuid
from pathlib import Path
from shutil import which
from socket import gethostname
from subprocess import DEVNULL, check_call
from typing import Any, Self

# THIS MODULE CANNOT CONTAIN ANY THIRD PARTY IMPORTS


_FORMAT = (
    f"[{{asctime}} ❯ {gethostname()} ❯ {{module}}:{{funcName}}:{{lineno}}] {{message}}"  # noqa: RUF001
)
basicConfig(format=_FORMAT, datefmt="%Y-%m-%d %H:%M:%S", style="{", level="INFO")
_LOGGER = getLogger(__name__)
_IS_ROOT = getuid() == 0
_SUDO = "" if _IS_ROOT else "sudo "
_REPO_URL = "https://github.com/dycw/test-remote-script.git"
_REPO_ROOT = Path("/tmp/test-remote-script")  # noqa: S108
__version__ = "0.1.6"


def _main() -> None:
    _LOGGER.info("Running entrypoint %s...", __version__)
    settings, args = _Settings.parse()
    _ensure_repo_cloned(settings.url, settings.path)
    _ensure_repo_version(settings.path, version=settings.version)
    _install_uv()
    cmd = " ".join(["uv run python3 -m test_remote_script.main", *args])
    _run(cmd, cwd=settings.path)
    _LOGGER.info("Running: %r", cmd)


@dataclass(order=True, unsafe_hash=True, kw_only=True, slots=True)
class _Settings:
    url: str = _REPO_URL
    path: Path = _REPO_ROOT
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
            "--repo-path", type=Path, default=_REPO_ROOT, help="Repo path", dest="path"
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


def _ensure_repo_version(path: Path | str, /, *, version: str | None = None) -> None:
    if version is None:
        return
    tag = _run("git describe --tags --exact-match", cwd=path)
    current = _run("git rev-parse --abbrev-ref HEAD", cwd=path) if tag == "" else tag
    if current == version:
        return
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


def _run(cmd: str, /, *, cwd: Path | str | None = None) -> None:
    _ = check_call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True, cwd=cwd)


if __name__ == "__main__":
    _main()
