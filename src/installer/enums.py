from __future__ import annotations

from enum import StrEnum, unique
from typing import assert_never

from installer.settings import SETTINGS


@unique
class Subnet(StrEnum):
    qrt = "qrt"
    main = "main"
    test = "test"

    @property
    def n(self) -> int:
        match self:
            case Subnet.qrt:
                return SETTINGS.subnets.qrt
            case Subnet.main:
                return SETTINGS.subnets.main
            case Subnet.test:
                return SETTINGS.subnets.test
            case never:
                assert_never(never)


__all__ = ["Subnet"]
