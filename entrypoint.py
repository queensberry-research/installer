#!/usr/bin/env python3
from __future__ import annotations

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from dataclasses import dataclass
from logging import basicConfig, getLogger
from pathlib import Path
from shutil import rmtree
from socket import gethostname
from subprocess import check_call
from typing import Any, Self

# THIS MODULE CANNOT CONTAIN ANY THIRD PARTY IMPORTS


_FORMAT = (
    f"[{{asctime}} ❯ {gethostname()} ❯ {{module}}:{{funcName}}:{{lineno}}] {{message}}"  # noqa: RUF001
)
basicConfig(format=_FORMAT, datefmt="%Y-%m-%d %H:%M:%S", style="{", level="INFO")
_LOGGER = getLogger(__name__)
_REPO_URL = "https://github.com/dycw/test-remote-script.git"
_REPO_ROOT = Path("/tmp/test-remote-script")  # noqa: S108
__version__ = "0.1.3"


def _main() -> None:
    _LOGGER.info("Running entrypoint %s...", __version__)
    settings, args = _Settings.parse()
    if (path := settings.root).is_dir():
        _LOGGER.info("Removing %r...", str(path))
        rmtree(path, ignore_errors=True)
    _LOGGER.info("Cloning %r to %r...", url := settings.url, str(path))
    _ = check_call(f"git clone {url} {path}")
    if (version := settings.version) is not None:
        _LOGGER.info("Switching %r to %r...", str(path), version)
        _ = check_call(f"git checkout {version}", cwd=path)
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


if __name__ == "__main__":
    _main()
