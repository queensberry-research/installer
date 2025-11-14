#!/usr/bin/env python3
from __future__ import annotations

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from dataclasses import dataclass
from logging import basicConfig, getLogger
from os import geteuid
from pathlib import Path
from shutil import rmtree, which
from socket import gethostname
from subprocess import DEVNULL, check_call
from typing import Any, Self

# THIS MODULE CANNOT CONTAIN ANY THIRD PARTY IMPORTS


_FORMAT = (
    f"[{{asctime}} ❯ {gethostname()} ❯ {{module}}:{{funcName}}:{{lineno}}] {{message}}"  # noqa: RUF001
)
basicConfig(format=_FORMAT, datefmt="%Y-%m-%d %H:%M:%S", style="{", level="INFO")
_LOGGER = getLogger(__name__)
_SUDO = geteuid() != 0
_REPO_URL = "https://github.com/dycw/test-remote-script.git"
_REPO_ROOT = Path("/tmp/test-remote-script")  # noqa: S108
__version__ = "0.1.4"


def _main() -> None:
    _LOGGER.info("Running entrypoint %s...", __version__)
    settings, args = _Settings.parse()
    if (path := settings.root).is_dir():
        _LOGGER.info("Removing %r...", str(path))
        rmtree(path, ignore_errors=True)
    _apt_install("git")
    _LOGGER.info("Cloning %r to %r...", url := settings.url, str(path))
    _run(f"git clone {url} {path}")
    if (version := settings.version) is not None:
        _LOGGER.info("Switching %r to %r...", str(path), version)
        _run(f"git checkout {version}", cwd=path)
    _install_uv()
    _LOGGER.info("Rest of the args: %s", args)


@dataclass(order=True, unsafe_hash=True, kw_only=True, slots=True)
class _Settings:
    url: str = _REPO_URL
    root: Path = _REPO_ROOT
    version: str | None = None

    @classmethod
    def parse(cls) -> tuple[Self, Any]:
        parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
        _ = parser.add_argument(
            "--repo-url", type=str, default=_REPO_URL, help="Repo URL", dest="url"
        )
        _ = parser.add_argument(
            "--repo-root", type=Path, default=_REPO_ROOT, help="Repo root", dest="root"
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


def _apt_install(cmd: str, /) -> None:
    if which(cmd) is not None:
        return
    _LOGGER.info("Updating 'apt'...")
    _run(f"{_SUDO} apt update -y")
    _LOGGER.info("Installing %r...", cmd)
    _run(f"{_SUDO} apt install -y {cmd}")


def _install_uv() -> None:
    if which("uv") is not None:
        return
    _apt_install("curl")
    _LOGGER.info("Installing 'uv'...")
    url = "https://astral.sh/uv/install.sh"
    path = Path("/usr/local/bin")
    _run(f"curl -LsSf {url} | env UV_INSTALL_DIR={path} UV_NO_MODIFY_PATH=1 sh")
    _run(f"chmod +x {path}/{{uv, uvx}}")


def _run(cmd: str, /, *, cwd: Path | str | None = None) -> None:
    _ = check_call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True, cwd=cwd)


if __name__ == "__main__":
    _main()
