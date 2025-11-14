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

    subnets: _Subnets
    downloads: _Downloads


class _Downloads(BaseSettings):
    timeout: int
    chunk_size: int


class _Subnets(BaseSettings):
    qrt: int
    main: int
    test: int


SETTINGS = load_settings(_Settings)


__all__ = ["SETTINGS"]
