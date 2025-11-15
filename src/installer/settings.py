from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar

from pydantic_settings import BaseSettings
from utilities.pydantic_settings import (
    CustomBaseSettings,
    PathLikeOrWithSection,
    load_settings,
)

from installer.constants import CONFIGS


class _Settings(CustomBaseSettings):
    toml_files: ClassVar[Sequence[PathLikeOrWithSection]] = [CONFIGS / "config.toml"]

    downloads: _Downloads
    ssh: _SSH
    subnets: _Subnets


class _Downloads(BaseSettings):
    timeout: int
    chunk_size: int


class _SSH(BaseSettings):
    known_hosts: list[_SSHKnownHost]
    max_tries: int


class _SSHKnownHost(BaseSettings):
    hostname: str
    port: int | None = None


class _Subnets(BaseSettings):
    qrt: int
    main: int
    test: int


SETTINGS = load_settings(_Settings)


__all__ = ["SETTINGS"]
